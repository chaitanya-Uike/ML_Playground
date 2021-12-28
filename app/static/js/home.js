const dropZone = document.querySelector("#drop_zone")
const header = document.querySelector(".header")
const input = document.querySelector("#file")
const button = document.querySelector("#browse-btn")
const info = document.querySelector("#info")
const csvHead = document.querySelector(".csv-head-div")
const metaInfo = document.querySelector(".meta-info")
const next = document.querySelector(".next")

const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value

let file
let closeSession = true

button.addEventListener("click", () => {
    input.click()
})

input.addEventListener("change", event => {
    file = event.target.files[0]
    dropZone.classList.add("active")
    uploadFile()
})

dropZone.addEventListener("dragover", event => {

    event.preventDefault()
    dropZone.classList.add("active")
    header.textContent = "Release to upload File"
})

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("active");
    header.textContent = "Drag csv file here"
});

dropZone.addEventListener("drop", event => {
    event.preventDefault()
    file = event.dataTransfer.files[0]
    uploadFile()
})

let session;

async function uploadFile() {
    let fileType = file.type
    if (fileType == "application/vnd.ms-excel") {
        const fd = new FormData()
        fd.append('file', file)

        header.textContent = "Uploading..."

        const response = await fetch('/app/home/', {
            method: "POST",
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: fd,
        })


        if (response.ok) {
            header.textContent = file.name
            info.classList.remove("hidden")
            info.textContent = "uploaded successfuly"

            metaInfo.classList.remove("hidden")

            const data = await response.json()

            session = data['session']


            dropZone.removeChild(document.querySelector("#or"))
            dropZone.removeChild(button)

            let sessionId = document.createElement("h4")
            sessionId.id = "session-id"
            sessionId.innerHTML = `session: ${session}`

            dropZone.appendChild(sessionId)

            // // setting up the initial values
            document.querySelector(".shape").textContent = `${data["shape"][0]} X ${data["shape"][1]}`
            document.querySelector("#n-rows").value = `${data["shape"][0]}`

            const res = await fetch(`/app/head/${session}/`)
            const head = await res.json()

            displayHead(JSON.parse(head))
        }

        else {
            header.textContent = "Some error Occurred"
        }
    }

    else {
        alert("please upload a CSV file!")
        dropZone.classList.remove("active")
        header.textContent = "Drag csv file here"
    }
}

function displayHead(head) {
    const table = document.createElement("table")

    table.classList.add("table")
    table.classList.add("table-hover")

    let thead = document.createElement("thead")
    let tr = document.createElement("tr")
    let idx = 0;
    for (let i = 0; i < Object.keys(head).length; i++) {
        let th = document.createElement("th")
        th.textContent = idx++ + ": " + Object.keys(head)[i]
        th.scope = "col"
        tr.appendChild(th)
    }
    thead.appendChild(tr)
    table.appendChild(thead)

    let tbody = document.createElement("tbody")
    for (let j = 0; j < 5; j++) {
        let values = document.createElement("tr")
        for (let i = 0; i < Object.values(head).length; i++) {
            let td = document.createElement("td")
            td.textContent = Object.values(head)[i][j]
            values.appendChild(td)
        }
        tbody.appendChild(values)
    }
    table.appendChild(tbody)
    csvHead.innerHTML = ""
    csvHead.appendChild(table)
}


window.onbeforeunload = function () {
    if (closeSession) {
        fetch(`/app/close-session/`, {
            method: "POST",
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                "session": session,
            }),
        })
    }
};

let catList
let dropList

next.addEventListener("click", async event => {

    if (event.target.id.split("-")[1] == 'drop_list') {

        dropList = document.getElementById(event.target.id.split("-")[1]).value.split(",")

        if (dropList[0] == '')
            dropList.pop()

        if (dropList.length > 0) {
            const res = await fetch(`/app/drop/${session}/`, {
                method: "POST",
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    "dropList": dropList,
                }),
            })

            if (res.ok) {
                const head = await res.json()
                displayHead(JSON.parse(head))
            }
        }

        event.target.id = "save-cat_list"
        document.querySelector(".cat_input").classList.remove("hidden")
    }

    else if (event.target.id.split("-")[1] == 'cat_list') {

        catList = document.getElementById(event.target.id.split("-")[1]).value.split(",")


        if (catList[0] == '')
            catList.pop()

        if (catList.length > 0) {
            const res = await fetch(`/app/encode/${session}/`, {
                method: "POST",
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    "catList": catList,
                    "dropList": dropList,
                }),
            })

            if (res.ok) {
                const head = await res.json()
                displayHead(JSON.parse(head))
            }
        }
        event.target.id = "save-all"
        document.querySelector(".other-inputs").style.display = "flex"
        next.innerHTML = "Start"
    }

    else {

        let n_samples = parseInt(document.querySelector("#n-rows").value)
        let X_start = parseInt(document.querySelector("#X_start").value)
        let X_end = parseInt(document.querySelector("#X_end").value)
        let Y_col = parseInt(document.querySelector("#Y_col").value)

        let classification = document.querySelector('input[name="classification"]:checked').value

        let n_class = parseInt(document.querySelector("#n_class").value)
        let test_size = parseInt(document.querySelector("#test_size").value)


        const res = await fetch(`/app/save-config/${session}/`, {
            method: "POST",
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                "n_samples": n_samples,
                "catList": catList,
                "dropList": dropList,
                "X_start": X_start,
                "X_end": X_end,
                "Y_col": Y_col,
                "classification": classification,
                "n_class": n_class,
                "test_size": test_size,
            }),
        })

        if (res.ok) {
            closeSession = false
            window.location.href = `/app/network/${session}/`;
        }

    }
})
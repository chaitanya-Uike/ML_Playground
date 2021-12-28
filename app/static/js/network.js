const networkContainer = document.querySelector(".network-container")
const svgContainer = document.querySelector(".svg-container")
const start = document.querySelector(".start-btn")
const download = document.querySelector("#download")


const config = JSON.parse(JSON.parse(document.getElementById('config').textContent))
const session = JSON.parse(document.getElementById('session').textContent)

const csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value

let inputDims = config['X_end'] + 1 - config['X_start']
let outputDims = config['n_class']
if (config['classification'] == 'binary')
    outputDims = 1

let layersDims = [inputDims, outputDims]

buildNetwork(layersDims)

function buildNetwork(layersDims) {

    let layers = layersDims.length

    clearNetwork()

    for (let i = 1; i <= layers; i++) {
        let layer = document.createElement("div")
        layer.className = "layer"

        if (i == 1 || i == layers)
            layer.innerHTML += `
            <input type="text" class="dims-input" id="dims-${i}"  value="4" disabled>
            `
        else
            layer.innerHTML += `
            <input type="number" class="dims-input" id="dims-${i}"  value="4" min=0 max=1000>`

        let neurons = document.createElement("div")
        neurons.className = "neurons"
        for (let j = 0; j < layersDims[i - 1]; j++) {
            if (j == 10)
                break
            if (layersDims[i - 1] > 10 && j == 8)
                neurons.innerHTML += `<div class="expanded"><i class="material-icons">more_vert</i></div>`
            else
                neurons.innerHTML += `
            <div class="neuron layer${i}"></div>`
        }
        layer.appendChild(neurons)
        networkContainer.appendChild(layer)

        if (i != layers && layersDims.length != 10) {
            let addLayerBtn = document.createElement("div")
            addLayerBtn.innerHTML = `
            <i class="material-icons">add</i>
            `
            addLayerBtn.className = "add-layer-btn"
            addLayerBtn.id = `${i + 1}`

            networkContainer.appendChild(addLayerBtn)
        }

        // if default number of neurons is changed
        document.getElementById(`dims-${i}`).value = layersDims[i - 1]
    }

    layersDimsInput()
    addHiddenLayerInput()

    let mainPadding = 10
    for (let layer = 1; layer < layers; layer++) {

        let layer1 = Array.from(document.getElementsByClassName(`layer${layer}`))
        let layer2 = Array.from(document.getElementsByClassName(`layer${layer + 1}`))

        for (let i = 0; i < layer1.length; i++) {
            for (let j = 0; j < layer2.length; j++) {
                svgContainer.innerHTML += `
            <line class="connection" 
            x1="${layer1[i].offsetLeft + 50}" 
            y1="${layer1[i].offsetTop + 25 - mainPadding}" 
            x2="${layer2[j].offsetLeft}" 
            y2="${layer2[j].offsetTop + 25 - mainPadding}"
            />
            `
            }
        }
    }
}

function clearNetwork() {
    Array.from(svgContainer.children).forEach(element => {
        element.remove()
    })

    networkContainer.innerHTML = ""
}


function layersDimsInput() {
    Array.from(document.getElementsByClassName("dims-input")).forEach(element => {
        element.addEventListener("change", event => {
            let id = event.target.id.split("-")[1]
            layersDims[id - 1] = parseInt(event.target.value)

            if (layersDims[id - 1] == 0)
                layersDims.splice(id - 1, 1)

            buildNetwork(layersDims)
        })
    })
}

function addHiddenLayerInput() {
    Array.from(document.getElementsByClassName("add-layer-btn")).forEach(element => {
        element.addEventListener("click", event => {
            let id = event.target.parentElement.id
            console.log(id);
            layersDims.splice(id - 1, 0, 4)

            buildNetwork(layersDims)
        })
    })
}

let trainCost = []
let testCost = []
let file_url

start.addEventListener("click", async event => {
    start.innerHTML = `
    <div class="spinner-border text-dark" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>`
    const res = await fetch(`/app/train/${session}/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
        body: JSON.stringify({
            "config": config,
            "layersDims": layersDims,
            "alpha": parseFloat(document.querySelector("#alpha").value),
            "epochs": parseFloat(document.querySelector("#epochs").value),
            "batch": parseFloat(document.querySelector("#batch").value),
            "beta1": parseFloat(document.querySelector("#beta1").value),
            "beta2": parseFloat(document.querySelector("#beta2").value),
            "lambda": parseFloat(document.querySelector("#lambda").value),
        })
    })

    start.innerHTML = `<i class="material-icons">play_arrow</i>`

    if (res.ok) {
        const data = await res.json()
        trainCost = data['train_cost']
        testCost = data['test_cost']
        file_url = data['file_url']

        download.setAttribute("href", file_url)

        document.querySelector("#a_train").innerHTML = `Training Accuracy: ${data['a_train'].toFixed(2)}`
        document.querySelector("#a_test").innerHTML = `Testing Accuracy: ${data['a_test'].toFixed(2)}`

        document.querySelector(".graph-container").style.display = "block"
        document.querySelector(".graph-container").scrollIntoView(false);
        costPlot()
    }
})


function costPlot() {
    var speedCanvas = document.getElementById("costChart");

    var dataFirst = {
        label: "train cost",
        data: trainCost,
        lineTension: 0,
        fill: false,
        borderColor: 'red'
    };

    var dataSecond = {
        label: "test cost",
        data: testCost,
        lineTension: 0,
        fill: false,
        borderColor: 'blue'
    };

    let labels = []
    for (let i = 0; i < parseFloat(document.querySelector("#epochs").value); i += 10) {
        labels.push(i)
    }

    var costData = {
        labels: labels,
        datasets: [dataFirst, dataSecond]
    };

    var chartOptions = {
        legend: {
            display: true,
            position: 'top',
            labels: {
                boxWidth: 80,
                fontColor: 'white'
            }
        }
    };

    var lineChart = new Chart(speedCanvas, {
        type: 'line',
        data: costData,
        options: chartOptions,
        scales: {
            x: {
                color: 'red',
            }
        }
    });
}
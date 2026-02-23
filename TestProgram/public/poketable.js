const downloadButton = document.getElementById('button-container');
const tableData = document.querySelector('table');


// Empty class gets automatically updated
class ObjTemplate {
    constructor(keys) {
        keys.forEach(header => {
            const result = sanitize(header.innerText);
            this[result] = '';
    });
    }
}


// Sanitizes headers and table data of spaces and punctuation
function sanitize(data) {
    let noSpace = data.replaceAll(/ /g,'_').toLowerCase();
    let noPunct = noSpace.replaceAll(/[\. \'\"]/g, '')
    return noPunct;
}


// Creates a new Object based on ObjTemplate and updates the key-values, 
// then returns the newly created Object
function createObj(objValues, objList) {
    const objKeys = tableData.querySelectorAll('th');
    let newObj = new ObjTemplate(objKeys);
    Object.keys(newObj).forEach((key, index) => {
        if (objValues[index]) {
            let value = objValues[index].innerText;
            newObj[key] = value;
        }
    })
    objList.push(newObj);
} 


function toJSON(tableData) {
    const tableRows = tableData.querySelectorAll('tr');
    let objList = [];
    tableRows.forEach((row, index) => {
        // skip over the header row because we don't want to create an extra Object
        if (index === 0) return;
        const objValues = row.querySelectorAll('td');
        createObj(objValues, objList);
    })
    return objList;
}


downloadButton.addEventListener('click', (event) => {
    const payload = {
        title: tableData.querySelector('caption').innerText.replaceAll(' ',''),
        filetype: event.target.id,
        data: toJSON(tableData)
    };
    console.log(payload)
    fetch('http://localhost:8000/file-download',{
        mode: 'cors',
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
})
.then(response => response.blob())
.then(blob => {
    // make blob object downloadable
    const objectURL = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = objectURL;
    // filename is table caption by default
    link.download = payload.title;
    // append link and add click event
    document.body.appendChild(link);
    link.click();

    // clean up after download
    document.body.removeChild(link);
    URL.revokeObjectURL(objectURL);
})
});
// categories is the main data structure for the app; it looks like this:

//  [
//    { title: "Math",
//      clues: [
//        {question: "2+2", answer: 4, showing: null},
//        {question: "1+1", answer: 2, showing: null}
//        ...
//      ],
//    },
//    { title: "Literature",
//      clues: [
//        {question: "Hamlet Author", answer: "Shakespeare", showing: null},
//        {question: "Bell Jar Author", answer: "Plath", showing: null},
//        ...
//      ],
//    },
//    ...
//  ]


/** Get NUM_CATEGORIES random category from API.
 *
 * Returns array of category ids
 */

async function getCategoryIds() {
    let catIds = []
    for (let i = 0; i < 6; i++) {
        let data = await axios.get('https://jservice.io/api/categories', {
            params: {
                count: 1,
                offset: Math.floor(Math.random() * 1000)
            }
        })
        // console.log(data.data[0]);
        if (data.data[0].clues_count < 5) { i-- }
        else { catIds.push(data.data[0]['id']); }
        // console.log(data);
    }
    // console.log(catIds);
    return catIds;
}

/** Return object with data about a category:
 *
 *  Returns { title: "Math", clues: clue-array }
 *
 * Where clue-array is:
 *   [
 *      {question: "Hamlet Author", answer: "Shakespeare", showing: null},
 *      {question: "Bell Jar Author", answer: "Plath", showing: null},
 *      ...
 *   ]
 */

async function getCategory(catIds) {
    let tableData = [];
    for (const i of catIds) {
        let newCat = await axios.get('https://jservice.io/api/category', {
            params: {
                id: i
            }
        });
        tableData.push(newCat.data);
    }
    // console.log(tableData);
    // Shuffles returned clues array and deletes unimportant data
    for (const i of tableData) {
        i.clues.sort(() => Math.random() - 0.5);
        i.clues.splice(5);
        delete i.clues_count;
    };
    return tableData;
}

/** Fill the HTML table#jeopardy with the categories & cells for questions.
 *
 * - The <thead> should be filled w/a <tr>, and a <td> for each category
 * - The <tbody> should be filled w/NUM_QUESTIONS_PER_CAT <tr>s,
 *   each with a question for each category in a <td>
 *   (initally, just show a "?" where the question/answer would go.)
 */


function fillTable(tableData) {
    // Create game table
    let table = document.createElement("table");
    table.setAttribute('id', 'gameboard');
    const gameArea = document.createElement('div')
    /*
    Instead of saving data as a property to the cell, creating and storing the data in a Map object and then subsequently returning it,
    will prevent the data being readily accessable to the client from the DOM as long as the Map object doesn't get added to the global scope.
    
        - Although this implementation is more secure than storing th data as properties in each cell, security can be improved upon with a backend.

        - Creating a backend would also be neccisary to make implementing other features, such as saving a game's progress, possible.
        
    */
    let cellDataMap = new Map();

    for (let topics of tableData) {
        let row = document.createElement("tr");
        let cell = document.createElement("td");
        cell.innerHTML = topics.title;
        // console.log(topics);
        row.append(cell);

        table.append(row);

        for (let clues of topics.clues) {
            cell = document.createElement("td");
            cell['state'] = 'unselected';
            cell.textContent = '?';
            row.append(cell);

            cellDataMap.set(cell, { row: topics.title, answer: clues['answer'], question: clues['question'] });

        }
    }
    gameArea.append(table);
    const resetBtn = document.createElement('button');
    resetBtn.innerText = 'Restart';
    resetBtn.setAttribute('id', 'resetBtn');
    resetBtn.addEventListener('click', handleClick);
    gameArea.append(resetBtn);

    document.querySelector('#gameArea').append(gameArea)
    return cellDataMap;

}

/** Handle clicking on a clue: show the question or answer.
 *
 * Uses .showing property on clue to determine what to show:
 * - if currently null, show question & set .showing to "question"
 * - if currently "question", show answer & set .showing to "answer"
 * - if currently "answer", ignore click
 * */

function handleClick(e) {
    e.target.parentNode.remove();
    setupAndStart();
}

/** Wipe the current Jeopardy board, show the loading spinner,
 * and update the button used to fetch data.
 */

// instead of having the loading view being manipulated by 2 seperate functions, I merged both functionalities into one function.
function toggleLoadingView(mode) {
    // Show loading animation
    if (mode === 'show') {
        document.getElementById('loadingSpinner').style.display = 'block';
    }
    // Hide loading animation
    else if (mode === 'hide') {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
}

/** Remove the loading spinner and update the button used to fetch data. */

// I found my solution to be simpler if the task done this function was completed by other functions.
function hideLoadingView() {
}

/** Start game:
 *
 * - get random category Ids
 * - get data for each category
 * - create HTML table
 * */

async function setupAndStart() {

    try {
        toggleLoadingView('show');
        const catIds = await getCategoryIds();
        const tableData = await getCategory(catIds);
        const cellDataMap = fillTable(tableData);
        gameLogic(cellDataMap);
        toggleLoadingView('hide');
    }
    catch {
        showErrorMsg();
    }
}

/** On click of start / restart button, set up game. */

// TODO
const startButton = document.querySelector('#startButton');
startButton.addEventListener('click', handleClick);

/** On page load, add event handler for clicking clues */

// TODO
function gameLogic(cellDataMap) {
    const gameboard = document.querySelector('#gameboard')
    gameboard.addEventListener('click', (e) => {
        const cell = e.target;
        if ('state' in cell) {
            const data = cellDataMap.get(cell);
            if (cell['state'] === 'unselected') {
                cell.innerHTML = data['question'];
                cell['state'] = 'selected';
            }
            else if (cell['state'] === 'selected') {
                cell.innerHTML = data['answer'];
                cell['state'] = 'answered';
            }
            // else { console.log('miss') };
        };
    });
};


// If an error occurs when requesting from the Api the following code will run

function showErrorMsg() {
    const gameArea = document.querySelector('#gameArea')
    const errordiv = document.createElement('div');
    const errorMsg = document.createElement('p');
    errorMsg.innerText = 'An error has occured. Please wait 30 seconds and try again.'
    const resetBtn = document.createElement('button');
    resetBtn.innerText = 'Restart';
    resetBtn.setAttribute('id', 'resetBtn');
    errordiv.append(errorMsg);
    errordiv.append(resetBtn);
    resetBtn.addEventListener('click', handleClick);
    gameArea.append(errordiv);
    toggleLoadingView('hide');
};
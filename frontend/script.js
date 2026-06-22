// document.getElementById("upload-form").addEventListener(
//     "submit",
//     async (e) => {

//         e.preventDefault();

//         const formData = new FormData();

//         formData.append(
//             "course",
//             document
//             .getElementById("course")
//             .value
//         );

//         formData.append(
//             "unit",
//             document
//             .getElementById("unit")
//             .value
//         );

//         formData.append(
//             "note_type",
//             document
//             .getElementById("note_type")
//             .value
//         );

//         const files =
//             document
//             .getElementById("files")
//             .files;

//         for (const file of files) {

//             formData.append(
//                 "file",
//                 file
//             );
//         }

//         const response =
//             await fetch(
//                 "http://127.0.0.1:8000/upload",
//                 {
//                     method: "POST",
//                     body: formData
//                 }
//             );

//         const data =
//             await response.json();

//         console.log(data);
//     }
// );

// ==========================
// LOAD WORKSPACE
// ==========================

async function loadWorkspace() {

    try {

        const res = await fetch(
            "http://localhost:8000/workspace"
        );

        if (!res.ok) {
            throw new Error(
                `HTTP Error: ${res.status}`
            );
        }

        const workspaceData =
            await res.json();

        const treeContainer =
            document.getElementById(
                "workspace-tree"
            );

        treeContainer.innerHTML = "";

        renderTree(
            workspaceData,
            treeContainer,
            ""
        );

    }

    catch (err) {

        console.error(
            "Workspace Load Error:",
            err
        );

    }

}

// ==========================
// TREE RENDERER
// ==========================

function renderTree(
    data,
    parent,
    currentPath = ""
) {

    for (const key in data) {

        const fullPath =
            currentPath
                ? `${currentPath}/${key}`
                : key;

        // FILE
        if (data[key] === null) {

            const file =
                document.createElement(
                    "div"
                );

            file.className = "file";

            file.textContent = key;

            file.dataset.path =
                fullPath;

            file.addEventListener(
                "click",
                () => {

                    loadFile(
                        fullPath
                    );

                }
            );

            parent.appendChild(file);

        }

        // FOLDER
        else {

            const folder =
                document.createElement(
                    "div"
                );

            folder.className =
                "folder";

            const header =
                document.createElement(
                    "div"
                );

            header.className =
                "folder-header";

            header.innerHTML =
                `<span class="arrow">▼</span> ${key}`;

            const content =
                document.createElement(
                    "div"
                );

            content.className =
                "folder-content";

            renderTree(
                data[key],
                content,
                fullPath
            );

            header.addEventListener(
                "click",
                () => {

                    folder.classList.toggle(
                        "closed"
                    );

                }
            );

            folder.appendChild(
                header
            );

            folder.appendChild(
                content
            );

            parent.appendChild(
                folder
            );

        }

    }

}

// ==========================
// CHAT PANEL TOGGLE
// ==========================

const toggleBtn =
    document.getElementById(
        "toggleChat"
    );

const chatPanel =
    document.getElementById(
        "chatPanel"
    );

toggleBtn.addEventListener(
    "click",
    () => {

        chatPanel.classList.toggle(
            "collapsed"
        );

        toggleBtn.innerHTML =
            chatPanel.classList.contains(
                "collapsed"
            )
                ? ">"
                : "<";

    }
);

// ==========================
// STARTUP
// ==========================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadWorkspace();

    }
);

async function loadFile(path){

    try{

        const res =
        await fetch(
            `http://localhost:8000/file?path=${encodeURIComponent(path)}`
        );

        if(!res.ok){

            throw new Error(
                "Failed to load file"
            );

        }

        const data =
        await res.json();

        document.querySelector(
            ".editor-content"
        ).innerHTML =

        `<pre>${data.content}</pre>`;

    }

    catch(err){

        console.error(err);

    }

}
function loadArtifact(name) {
    fetch(`artifact/${name}/`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Ошибка: " + data.error);
            } else {
                showCodeEditor(data.query_vql);
            }
        })
        .catch(error => console.error("Ошибка загрузки:", error));
}

function showCodeEditor(code) {
    document.getElementById("code-editor-container").style.display = "block";
    if (window.editor) {
        window.editor.setValue(code);
    } else {
        window.editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
            mode: "yaml",
            theme: "eclipse",
            lineNumbers: true,
        });
        window.editor.setValue(code);
    }
}

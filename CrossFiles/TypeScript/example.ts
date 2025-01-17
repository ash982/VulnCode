<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TypeScript User Input Example</title>
</head>
<body>
    <h2>Enter your name:</h2>
    <input type="text" id="userInput" placeholder="Type your name here">
    <button id="submitBtn">Submit</button>
    
    <h3>Output:</h3>
    <p id="outputText"></p>

    <script type="module">
        // TypeScript Code in HTML
        function displayText(): void {
            let inputElement = document.getElementById("userInput") as HTMLInputElement;
            let outputElement = document.getElementById("outputText") as HTMLElement;

            if (inputElement && outputElement) {
                outputElement.innerText = "Hello, " + inputElement.value + "!";
            }
        }

        // Add event listener to the button
        document.getElementById("submitBtn")?.addEventListener("click", displayText);
    </script>

</body>
</html>

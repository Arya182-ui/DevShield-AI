const vscode = require('vscode');
const fetch = require('node-fetch');

function getSettingsHtml(apiKey) {
    if (!apiKey) {
        return `
            <html>
            <body style="font-family: sans-serif;">
                <h2>DevShield Settings</h2>
                <p>No API Key found. Please login or register.</p>
                <button onclick="login()">Login/Register</button>
                <script>
                    function login() {
                        window.acquireVsCodeApi().postMessage({ type: 'login' });
                    }
                </script>
            </body>
            </html>
        `;
    } else {
        return `
            <html>
            <body style="font-family: sans-serif;">
                <h2>DevShield Settings</h2>
                <p><b>API Key:</b></p>
                <input type="text" id="apikey" value="${apiKey}" style="width: 80%;" readonly />
                <button onclick="copyApiKey()">Copy</button>
                <br/><br/>
                <button onclick="logout()">Logout</button>
                <script>
                    function copyApiKey() {
                        const input = document.getElementById('apikey');
                        input.select();
                        document.execCommand('copy');
                        alert('API Key copied!');
                    }
                    function logout() {
                        window.acquireVsCodeApi().postMessage({ type: 'logout' });
                    }
                </script>
            </body>
            </html>
        `;
    }
}
function showSettingsWebview(context) {
    const panel = vscode.window.createWebviewPanel(
        'devshieldSettings',
        'DevShield Settings',
        vscode.ViewColumn.One,
        { enableScripts: true }
    );
    context.secrets.get('devshield-api-key').then(apiKey => {
        panel.webview.html = getSettingsHtml(apiKey);
    });
    panel.webview.onDidReceiveMessage(async message => {
        if (message.type === 'logout') {
            await context.secrets.delete('devshield-api-key');
            vscode.window.showInformationMessage('DevShield: Logged out. Please login again.');
            panel.dispose();
        }
        if (message.type === 'login') {
            // Trigger login flow
            await getApiKey(context);
            // Refresh webview after login
            const apiKey = await context.secrets.get('devshield-api-key');
            panel.webview.html = getSettingsHtml(apiKey);
        }
    });
}





function activate(context) {
    console.log("DevShield extension activated");
    // Command: manual scan
    let disposable = vscode.commands.registerCommand('devshield.scanDocument', async function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;
        const text = editor.document.getText();
        const secrets = scanTextForSecrets(text);
        if (secrets.length > 0) {
            for (const secret of secrets) {
                await analyzeWithBackend(context, secret, editor.document.fileName, 1);
            }
        } else {
            vscode.window.showInformationMessage('DevShield: No secrets detected!');
        }
    });
    context.subscriptions.push(disposable);

    // Command: settings UI
    let settingsCmd = vscode.commands.registerCommand('devshield.settings', function () {
        showSettingsWebview(context);
    });
    context.subscriptions.push(settingsCmd);

    // On save: scan document
    vscode.workspace.onWillSaveTextDocument(async event => {
        const text = event.document.getText();
        const secrets = scanTextForSecrets(text);
        if (secrets.length > 0) {
            for (const secret of secrets) {
                await analyzeWithBackend(context, secret, event.document.fileName, 1);
            }
        }
    });

    // On paste: scan clipboard
    vscode.commands.registerCommand('type', async args => {
        if (args && typeof args.text === 'string') {
            const secrets = scanTextForSecrets(args.text);
            if (secrets.length > 0) {
                for (const secret of secrets) {
                    await analyzeWithBackend(context, secret, 'clipboard', 1);
                }
            }
        }
        return vscode.commands.executeCommand('default:type', args);
    });
}

function deactivate() {}

module.exports = { activate, deactivate };


// Advanced regex patterns for secrets
const SECRET_PATTERNS = [
    /api[_-]?key\s*=\s*['"][A-Za-z0-9_\-]{16,}['"]/i,
    /secret[_-]?key\s*=\s*['"][A-Za-z0-9_\-]{16,}['"]/i,
    /password\s*=\s*['"][^'"]{8,}['"]/i,
    /token\s*=\s*['"][A-Za-z0-9_\-]{16,}['"]/i,
    /aws[_-]?(access|secret)?[_-]?key(id)?\s*=\s*['"][A-Za-z0-9\/+=]{20,40}['"]/i,
    /google[_-]?api[_-]?key\s*=\s*['"][A-Za-z0-9_\-]{20,40}['"]/i,
    /jwt\s*=\s*['"][A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+['"]/i,
    /-----BEGIN (RSA|DSA|EC|OPENSSH|PRIVATE) KEY-----[\s\S]+?-----END (RSA|DSA|EC|OPENSSH|PRIVATE) KEY-----/i
];

// Entropy check (Shannon entropy)
function shannonEntropy(str) {
    const map = {};
    for (let i = 0; i < str.length; i++) {
        map[str[i]] = (map[str[i]] || 0) + 1;
    }
    let entropy = 0;
    for (let k in map) {
        const p = map[k] / str.length;
        entropy -= p * Math.log2(p);
    }
    return entropy;
}


async function getApiKey(context) {
    let apiKey = await context.secrets.get('devshield-api-key');
    if (!apiKey) {
        const choice = await vscode.window.showQuickPick(['Login', 'Register'], { placeHolder: 'DevShield: Login or Register?' });
        if (!choice) {
            vscode.window.showErrorMessage('DevShield: Login/Register cancelled.');
            return null;
        }
        const email = await vscode.window.showInputBox({ prompt: 'Enter your email for DevShield AI' });
        if (!email) {
            vscode.window.showErrorMessage('DevShield: Email required.');
            return null;
        }
        const password = await vscode.window.showInputBox({ prompt: 'Enter your password', password: true });
        if (!password) {
            vscode.window.showErrorMessage('DevShield: Password required.');
            return null;
        }
        try {
            let url = 'http://localhost:8000/api/login';
            let body = { email, password };
            if (choice === 'Register') {
                url = 'http://localhost:8000/api/register';
                body = { email, password };
            }
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await res.json();
            if (data.api_key) {
                await context.secrets.store('devshield-api-key', data.api_key);
                vscode.window.showInformationMessage('DevShield: Login/Register successful!');
                apiKey = data.api_key;
            } else {
                vscode.window.showErrorMessage('DevShield: ' + (data.error || 'Login/Register failed.'));
                return null;
            }
        } catch (err) {
            vscode.window.showErrorMessage('DevShield: Login/Register error: ' + err.message);
            return null;
        }
    }
    return apiKey;
}


function scanTextForSecrets(text) {
    let results = [];
    SECRET_PATTERNS.forEach(pattern => {
        let match;
        let regex = new RegExp(pattern, 'gi');
        while ((match = regex.exec(text)) !== null) {
            results.push({
                match: match[0],
                index: match.index,
                entropy: shannonEntropy(match[0])
            });
        }
    });
    // High-entropy string detection (likely secrets)
    const highEntropyPattern = /['"][A-Za-z0-9\/+=]{16,}['"]/g;
    let match;
    while ((match = highEntropyPattern.exec(text)) !== null) {
        const value = match[0].replace(/['"]/g, '');
        const entropy = shannonEntropy(value);
        if (entropy > 3.5) {
            results.push({
                match: match[0],
                index: match.index,
                entropy
            });
        }
    }
    return results;
}

async function analyzeWithBackend(context, secret, fileName, line) {
    const apiKey = await getApiKey(context);
    if (!apiKey) return;
    try {
        const res = await fetch('http://localhost:8000/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey
            },
            body: JSON.stringify({
                pattern_type: 'Secret',
                variable_name: secret.match,
                filename: fileName,
                line: line || 1
            })
        });
        const data = await res.json();
        if (data.action === 'block') {
            vscode.window.showErrorMessage('DevShield: BLOCKED! ' + data.explanation);
        } else if (data.action === 'warn') {
            vscode.window.showWarningMessage('DevShield: Warning! ' + data.explanation);
        } else {
            vscode.window.showInformationMessage('DevShield: ' + data.explanation);
        }
    } catch (err) {
        vscode.window.showErrorMessage('DevShield: Backend error: ' + err.message);
    }
}




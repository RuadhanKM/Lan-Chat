import './App.css';

function App() {
	var name = ''
	window.ip = 'ws://10.167.149.16:8080'
	var lastUpdate = 0
	var missedMessages = 0
	
	function sendMessage(){
		document.getElementById("te").value = document.getElementById("te").value.replaceAll('\n', '')
		if (document.getElementById("te").value !== '' && name !== '') {
			let wss = new WebSocket(window.ip)
			wss.onopen = function(){
				wss.send("POST")
				wss.send(name)
				wss.send(document.getElementById("te").value)
				wss.send(document.getElementById("channel").value)
				document.getElementById("te").value = ''
				wss.close()
			}
		}
		missedMessages = 0
		document.querySelector("head > title").textContent = name
	}
	
	function getMessages(){
		let wsr = new WebSocket(window.ip)
		wsr.onopen = function(){
			wsr.send("GET")
			wsr.send(document.getElementById("channel").value)
			wsr.onmessage = function(event) {
				if (lastUpdate !== event.data){
					lastUpdate = event.data
					document.getElementById("mes").innerHTML = event.data
					document.getElementById("mes").scrollTop = document.getElementById("mes").scrollHeight
					if (!document.hasFocus()){
						missedMessages++
						document.querySelector("head > title").textContent = name + " [" + missedMessages.toString() + "]"
					}
				}
				wsr.close()
			}
		}
	}
	
	function confName(){
		if (document.getElementById("name").value.trim() !== '') {
			name = document.getElementById("name").value.trim()
			document.getElementById("name").remove()
			document.getElementById("nameSub").remove()
			document.getElementById("send").innerHTML = 'Send'
			document.querySelector("head > title").textContent = name
		}
	}
	
	function getOnline(){
		let wso = new WebSocket(window.ip)
		wso.onopen = function(){
			wso.send("ONLINE")
			wso.onmessage = function(event){
				document.getElementById("onl").innerHTML = event.data
				wso.close()
			}
		}
	}
	
	document.addEventListener("keydown", function(event) {
		if (event.keyCode === 13) {
			sendMessage()
		}
	})
	
	setInterval(getOnline, 3000)
	setInterval(getMessages, 1000)
	
	return (
		<div className="App">
			<div id={"mes"} className={"mesStlye"}></div>
			<div id={"onl"} className={"onlStlye"}></div>
			<textarea id={"te"} className={"tbStyle"} placeholder="Message..."></textarea>
			<textarea id={"name"} className={"nameStlye"} placeholder="Name..."></textarea>
			<textarea id={"channel"} className={"chanStyle"} maxlength="10" placeholder="Channel..."></textarea>
			<button id={"send"} className={"sbStyle"} onClick={sendMessage}>Enter a name first!</button>
			<button id={"nameSub"} className={"nameSubStlye"} onClick={confName}>Enter</button>
		</div>
	);
}

export default App;

import { useState } from "react";

function LoginPage() {
  const [text, setText] = useState("");

  const submit = () => fetch(`http://localhost:8001/login?username=${username.value}&password=${password.value}`)
  .then((response) => setText(response.ok ? "successful" : "unsuccessful"));

  return (
    <div>
      <label>login</label>
      <input id="username" placeholder="user" />
      <input id="password" placeholder="password" />
      <button onClick={submit}>Submit</button>
      <p>{text}</p>
    </div>
  );
}

export default LoginPage;
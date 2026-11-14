import { useState } from "react";

function RegisterPage() {
  const [text, setText] = useState("");

  const submit = () =>
    fetch(
      `http://localhost:8001/register?username=${registerUsername.value}&password=${registerPassword.value}&user_type=${registerRole.value}`,
      { method: "POST" }
    ).then((response) =>
      setText(response.ok ? "registered successfully" : "username already exists")
    );

  return (
    <div>
      <label>register</label>
      <input id="registerUsername" placeholder="user" />
      <input id="registerPassword" placeholder="password" type="password" />
      <input id="registerRole" placeholder="user or admin" />
      <button onClick={submit}>Submit</button>
      <p>{text}</p>
    </div>
  );
}

export default RegisterPage;
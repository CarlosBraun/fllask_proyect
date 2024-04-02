const express = require("express");
const connection = require("./database");
const app = express();
const port = 5000; // Puerto en el que se ejecutará el servidor
let v1 = connection.host;
// Ruta de prueba
app.get("/", (req, res) => {
  res.send("¡Hola, mundo! ${connection.host}" + v1);
});

// Iniciar el servidor
app.listen(port, () => {
  console.log(
    `Servidor escuchando en http://localhost:${port} de ${connection.host}`
  );
});

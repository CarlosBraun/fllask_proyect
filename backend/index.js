const express = require("express");
const connection = require("./database");
const app = express();
const PORT = process.env.PORTlet v1 = connection.host;
// Ruta de prueba
app.get("/", (req, res) => {
  res.send("¡Hola, mundo! prueba 1");
});
app.listen(PORT, () => {
  console.log(`Servidor escuchando en http://localhost:${port}`);
});

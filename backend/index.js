const express = require("express");
const connection = require("./database");
const cors = require("cors");
const app = express();
const PORT = process.env.PORT;
let v1 = connection.host;
// Ruta de prueba
app.use(cors());
app.get("/", (req, res) => {
  res.send("¡Hola, mundo! prueba 1");
});
app.listen(PORT, () => {
  console.log(`Servidor escuchando en http://localhost:${PORT}`);
});

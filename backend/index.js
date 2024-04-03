const express = require("express");
const connection = require("./database");
const bodyParser = require("body-parser");
const cors = require("cors");
const app = express();
const PORT = process.env.PORT;
const tablasRouter = require("./routes/tablas.router");
const formularioRouter = require("./routes/formulario.router");
// Ruta de prueba
app.use(cors());
app.use(bodyParser.json());
app.use("/tablas/", tablasRouter);
app.use("/formulario/", formularioRouter);
app.get("/", (req, res) => {
  res.send("Api online");
});
app.listen(5000, () => {
  console.log(`Servidor escuchando en http://localhost:5000`);
});

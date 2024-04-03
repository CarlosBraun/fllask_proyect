const express = require("express");
const connection = require("./database");
const bodyParser = require("body-parser");
const cors = require("cors");
const app = express();
const PORT = process.env.PORT;
const tablasRouter = require("./routes/tablas.router");
const formularioRouter = require("./routes/formulario.router");
const busquedaRouter = require("./routes/busqueda.router");
// Ruta de prueba
app.use(cors());
app.use(bodyParser.json());
app.use("/tablas/", tablasRouter);
app.use("/formulario/", formularioRouter);
app.use("/busqueda/", busquedaRouter);
app.get("/", (req, res) => {
  // HTML de ejemplo
  const htmlContent = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Document</title>
    </head>
    <body>
      <h1>Hello, World!</h1>
      <p>This is a test HTML response from Express.</p>
    </body>
    </html>
  `;

  // Enviar la respuesta con el HTML
  res.send(htmlContent);
});
app.listen(5000, () => {
  console.log(`Servidor escuchando en http://localhost:5000`);
});

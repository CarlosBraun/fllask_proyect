const mysql = require("mysql2/promise");

// Configuración de la conexión a la base de datos
const connection = mysql.createConnection({
  host: "flask-g19-miuandes-3b9d.a.aivencloud.com",
  user: "avnadmin",
  password: "AVNS_LHyyUux2JxRT64CsmA5",
  database: "defaultdb",
  port: "18573",
});

module.exports = connection;

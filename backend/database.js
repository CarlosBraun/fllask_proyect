const mysql = require("mysql2/promise");

// Configuracion para obtener una pool de conecciones
const pool = mysql.createPool({
  host: "flask-g19-miuandes-3b9d.a.aivencloud.com", //process.env.DB_HOST,
  user: "avnadmin", //process.env.DB_USER,
  password: "AVNS_LHyyUux2JxRT64CsmA5", //process.env.DB_PASSWORD,
  database: "defaultdb", //process.env.DB_NAME,
  port: 18573, //Number(process.env.DB_PORT),
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

module.exports = pool;
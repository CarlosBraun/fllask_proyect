const express = require("express");
const router = express.Router();
const cors = require("cors");

const tablasController = require("../controllers/tablas.controller");

router.use(
  cors({
    allowedOrigins: ["*"],
  })
);

router.post("/tabla1", tablasController.createFormularioTable);
router.post("/tabla2", tablasController.createEnajenanteTable);
router.post("/tabla3", tablasController.createAdquirenteTable);

module.exports = router;

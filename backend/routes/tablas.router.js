const express = require("express");
const router = express.Router();
const cors = require("cors");

const tablasController = require("../controllers/tablas.controller");

router.use(
  cors({
    allowedOrigins: ["*"],
  })
);

router.get("/tabla1", tablasController.createFormularioTable);
router.get("/tabla2", tablasController.createEnajenanteTable);
router.get("/tabla3", tablasController.createAdquirenteTable);
router.get("/tablas", tablasController.showtablas);

module.exports = router;

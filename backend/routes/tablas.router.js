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
router.get("/tablas1", tablasController.showtablas1);
router.get("/tablas2", tablasController.showtablas2);
router.get("/tablas3", tablasController.showtablas3);
router.get("/deltablas1", tablasController.deltablas1);
router.get("/deltablas2", tablasController.deltablas2);
router.get("/deltablas3", tablasController.deltablas3);

module.exports = router;

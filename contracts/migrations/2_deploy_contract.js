const libra = artifacts.require("./Libra");

module.exports = function (deployer) {
    deployer.deploy(libra);
};

const keccak256 = require('keccak256');

const libra = artifacts.require('./Libra');

contract("libra test", async () => {
    it("check if a transaction exists", async () => {
        let signed_tx = '0xd21a060154bac336027dfcdfabc161302d26d1d16ef085728abda1b8cafd0270';
        let state_root = '0x46e8ebcbe3a6a60ff09e0d37e9713d420449e0b3101cc21a63156dc04328a61b';
        let event_root = '0x3d0d96468f16e3dcbae00bfc75507f2838a52b248b3d0588ec886ab934020aaa';
        let root = '0x52833b815c6ec46c280a3813721711a306e180f5c1418a6908c7ac00616a052e';
        let proof = [
            '0x20d0eec6a73908bf3b531be94cb882b1e7ef7d94afb317691d5234b60efea887',
            '0xe1f72bd1816ed44839410e8efaa5efc26e43b1a63732744e6f18b7da22098611',
        ];
        let tx_version = 20;
        let bitmap = 20;

        let instance = await libra.deployed();
        let result = await instance.doesTxExist(signed_tx, state_root, event_root, root, proof, tx_version, bitmap);
        assert.equal(result, true, 'transaction should exist')
    });
});

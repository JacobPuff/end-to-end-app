const path = require('path');

module.exports = {
    mode: 'development',
    entry: {
        "login-signup": './src/login-signup.js',
        verify: './src/verify.js',
        forgotpassword: './src/forgotpassword.js',
        homePage: './src/homePage.js',
        tasklists: './src/tasklists/tasklists.js'
    },
    devtool: 'eval',
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, 'dist'),
    },
};
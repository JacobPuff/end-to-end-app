const path = require('path');

module.exports = {
    mode: 'development',
    entry: {
        tasklists: './src/tasklists/tasklists.js'
    },
    devtool: 'eval',
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, 'dist'),
    },
};
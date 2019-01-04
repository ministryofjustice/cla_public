var UnminifiedWebpackPlugin = require('unminified-webpack-plugin');
var UglifyJsPlugin = require('uglifyjs-webpack-plugin');
var common = {
      mode: 'production',
      output: {filename: 'cla.min.js'},
      target: 'web',
      optimization: {
        minimizer: [new UglifyJsPlugin({
            uglifyOptions: {
                compress: false,
                output: {
                    comments: false,
                },
            }
        })],
      },
      plugins: [
          new UnminifiedWebpackPlugin()
      ]
}

module.exports = common;

var webpack       = require('webpack');
var merge         = require('webpack-merge');
var autoprefixer  = require('autoprefixer');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var path = require('path');

var TARGET = process.env.npm_lifecycle_event;
process.env.BABEL_ENV = TARGET;

var target = __dirname + '/wagtailautocomplete/static/wagtailautocomplete/';

var STATIC_URL = process.env.STATIC_URL || '/static/';
var sassData = '$static-url: "' + STATIC_URL + '";';
console.log('Using STATIC_URL', STATIC_URL);


var common = {
	entry: {
		dist: __dirname + '/client/src/index.js',
	},

	output: {
		path: target,
		filename: '[name].js'
	},

	resolve: {
		extensions: ['.js'],
		modules: ['node_modules']
	},

	module: {
		rules: [
			{
				test: /\.js$/,
				use: [
					{
						loader: 'babel-loader',
						query: {
							presets: ['react', 'env'],
							plugins: ['add-module-exports']
						},
					}
				],
				include: [
					path.join(__dirname, '/client/'),
				],
			},
			{
				test: /\.s[ca]ss$/,
				use: ExtractTextPlugin.extract({
					fallback: 'style-loader',
					use: [
						'css-loader',
						'postcss-loader',
						{
							loader: 'sass-loader',
							options: {
								includePaths: [path.resolve(__dirname, 'node_modules/')],
								data: sassData
							}
						}
					]
				}),
			},
			{
				test: /\.css$/,
				use: ExtractTextPlugin.extract({
					fallback: 'style-loader',
					use: [
						'css-loader',
						'postcss-loader'
					]
				})
			}
		]
	},

	plugins: [
		new ExtractTextPlugin({
			filename: (getPath) => {
				return getPath('[name].css');
			}
		}),
	]
};

if (TARGET === 'build') {
	module.exports = merge(common, {
		plugins: [
			new webpack.DefinePlugin({
				'process.env': { 'NODE_ENV': JSON.stringify('production') }
			})
		]
	});
}

if (TARGET === 'start') {
	module.exports = merge(common, {
		devtool: 'eval-source-map',
		devServer: {
			contentBase: target,
			progress: true,
		}
	});
}

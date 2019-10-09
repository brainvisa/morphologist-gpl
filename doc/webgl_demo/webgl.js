var gl;

function init_gl(canvas)
{
	try {
		gl = canvas.getContext("experimental-webgl");
		gl.viewportWidth = canvas.width;
		gl.viewportHeight = canvas.height;
	} catch (e) {
	}
	if (!gl) {
		alert("Could not initialise WebGL, sorry :-(");
	}
	gl.getExtension("OES_standard_derivatives");
}

function get_file(path)
{
	var XHR = new XMLHttpRequest();
	XHR.open("GET", path, false);

	if(XHR.overrideMimeType){
		XHR.overrideMimeType("text/plain");
	}

	try{
		XHR.send(null);
	}catch(e){
		alert('Error reading file "' + path + '"\n' + e);
	}

	return XHR.responseText;
}

function load_shader_from_str(str, type)
{
	var shader;
	if (type == "x-shader/x-fragment") {
		shader = gl.createShader(gl.FRAGMENT_SHADER);
	} else if (type == "x-shader/x-vertex") {
		shader = gl.createShader(gl.VERTEX_SHADER);
	} else {
		return null;
	}

	gl.shaderSource(shader, str);
	gl.compileShader(shader);

	if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
		alert(gl.getShaderInfoLog(shader));
		return null;
	}

	return shader;
}

function load_shader_from_file(path, type)
{
	var str = get_file(path);
	return load_shader_from_str(str, type);
}


function load_shader_from_script(id)
{
	var shaderScript = document.getElementById(id);
	if (!shaderScript) {
		return null;
	}

	var str = "";
	var k = shaderScript.firstChild;
	while (k) {
		if (k.nodeType == 3) {
			str += k.textContent;
		}
		k = k.nextSibling;
	}
	return load_shader_from_str(str, shaderScript.type);
}

function init_shaders_from_id(vertexShader, fragmentShader)
{
	shader_program = gl.createProgram();
	gl.attachShader(shader_program, vertexShader);
	gl.attachShader(shader_program, fragmentShader);
	gl.linkProgram(shader_program);

	if (!gl.getProgramParameter(shader_program, gl.LINK_STATUS)) {
		alert("Could not initialise shaders");
	}

	gl.useProgram(shader_program);

	// position
	var aVertexPosition = gl.getAttribLocation(shader_program,
						"vertexPosition");
	gl.enableVertexAttribArray(aVertexPosition);

	// normal
	var aVertexNormal = gl.getAttribLocation(shader_program,
						"vertexNormal");
	gl.enableVertexAttribArray(aVertexNormal);

	// color
	var aVertexColor = gl.getAttribLocation(shader_program, "vertexColor");
	gl.enableVertexAttribArray(aVertexColor);

	// model matrix
	var uModelMatrix = gl.getUniformLocation(shader_program, "modelMatrix");
	var modelMatrix = mat4.identity();
	gl.uniformMatrix4fv(uModelMatrix, false, modelMatrix);

	// model matrix IT
	var uModelMatrixIT = gl.getUniformLocation(shader_program,
						"modelMatrixIT");
	var modelMatrixIT = mat4.identity();
	gl.uniformMatrix4fv(uModelMatrixIT, false, modelMatrixIT);

	// view matrix
	var uViewMatrix = gl.getUniformLocation(shader_program, "viewMatrix");
	var viewMatrix = mat4.identity();
	gl.uniformMatrix4fv(uViewMatrix, false, viewMatrix);

	// view matrix IT
	var uViewMatrixIT = gl.getUniformLocation(shader_program,
						"viewMatrixIT");
	var viewMatrixIT = mat4.identity();
	gl.uniformMatrix4fv(uViewMatrixIT, false, viewMatrixIT);

	// perspective matrix
	var uPerspectiveMatrix = gl.getUniformLocation(shader_program,
						"perspectiveMatrix");
	var perspectiveMatrix = mat4.ortho(-1, 1, -1, 1, 1, 30.); //FIXME
	//var perspectiveMatrix = mat4.frustum(-0.2, 0.2, -0.2, 0.2, 2, 30.); //FIXME
	gl.uniformMatrix4fv(uPerspectiveMatrix, false, perspectiveMatrix);

	return shader_program;
}

function init_shaders_from_files(vert, frag)
{
	var vertexShader = load_shader_from_file(vert, "x-shader/x-vertex");
	var fragmentShader = load_shader_from_file(frag, "x-shader/x-fragment");

	return init_shaders_from_id(vertexShader, fragmentShader);
}

function init_shaders_from_script(vert, frag)
{
	var vertexShader = load_shader_from_script(vert);
	var fragmentShader = load_shader_from_script(frag);

	return init_shaders_from_id(vertexShader, fragmentShader);
}

function set_view_matrix(viewMatrix)
{
	var uViewMatrix = gl.getUniformLocation(shader_program, "viewMatrix");
	gl.uniformMatrix4fv(uViewMatrix, false, viewMatrix);
	
	
	viewMatrixIT = mat4.inverse(mat4.transpose(viewMatrix));
	var uViewMatrixIT = gl.getUniformLocation(shader_program,
						"viewMatrixIT");
	gl.uniformMatrix4fv(uViewMatrixIT, false, viewMatrixIT);
}

function Object(vbo, ibo, nbo, cbo, modelMatrix, modelMatrixIT)
{
	this.vbo = vbo;
	this.ibo = ibo;
	this.nbo = nbo;
	this.cbo = cbo;
	this.modelMatrix = modelMatrix;
	if (modelMatrixIT == null)
		this.modelMatrixIT = mat4.inverse(mat4.transpose(modelMatrix));
	else	this.modelMatrixIT = modelMatrixIT
}

function draw_objects(shader_program, objects)
{
	gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

	for (i = 0; i < objects.length; ++i)
		draw_object(shader_program, objects[i]);
}

function draw_object(shader_program, obj)
{
	// vertices
	gl.bindBuffer(gl.ARRAY_BUFFER, obj.vbo);
	var aVertexPosition = gl.getAttribLocation(shader_program,
						"vertexPosition");
	gl.vertexAttribPointer(aVertexPosition, 3.0, gl.FLOAT, false, 0, 0);

	// normals
	if (obj.nbo != '')
	{
		gl.bindBuffer(gl.ARRAY_BUFFER, obj.nbo);
		var aVertexNormal = gl.getAttribLocation(shader_program,
						"vertexNormal");
	        gl.vertexAttribPointer(aVertexNormal, 3.0,
					gl.FLOAT, false, 0, 0);

		// matrice use to transform normals
		var uModelMatrixIT = gl.getUniformLocation(shader_program,
							"modelMatrixIT");
		gl.uniformMatrix4fv(uModelMatrixIT, false, obj.modelMatrixIT);
	}

	// colors
	gl.bindBuffer(gl.ARRAY_BUFFER, obj.cbo);
	var aVertexColor = gl.getAttribLocation(shader_program,
						"vertexColor");
	gl.vertexAttribPointer(aVertexColor, 4.0,gl.FLOAT, false, 0, 0);

	// model Matrix
	if (obj.modelMatrix != '')
	{
		var uModelMatrix = gl.getUniformLocation(shader_program,
							"modelMatrix");
		gl.uniformMatrix4fv(uModelMatrix, false, obj.modelMatrix);
	}

	// draw
	if (obj.ibo != '') // indiced triangles or ordred triangle
	{
		gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, obj.ibo);
		gl.drawElements(gl.TRIANGLES, obj.ibo.size,
					gl.UNSIGNED_SHORT, 0);
	}
	else
	{
		gl.drawArrays(gl.TRIANGLE_STRIP, 0, obj.vbo.size);
	}
}

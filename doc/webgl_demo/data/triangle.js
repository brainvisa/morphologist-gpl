function load_objects()
{
	// vertices
	var vbo = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, vbo);
	var vertices = new Float32Array([
			-1.0, -1.0, 0.0,
		 	-1.0,  1.0, 0.0,
			 1.0,  1.0, 0.0]);
	gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
	vbo.size = vertices.length / 3.0;

	// colors
	var cbo = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, cbo);
	var colors = new Float32Array([
			1.0, 0.0, 0.0, 1.0,
			0.0, 1.0, 0.0, 1.0,
			0.0, 0.0, 1.0, 1.0]);
	gl.bufferData(gl.ARRAY_BUFFER, colors, gl.STATIC_DRAW);
	cbo.size = colors.length / 4.0;

	// model matrix
	var modelMatrix = mat4.identity();

	ibo = nbo = '';
	return [new Object(vbo, ibo, nbo, cbo, modelMatrix)];
}

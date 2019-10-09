function load_objects()
{
	// vertices
	var vbo = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, vbo);
	var vertices = new Float32Array([
			// Front face
			-1.0, -1.0,  1.0,
			1.0, -1.0,  1.0,
			1.0,  1.0,  1.0,
			-1.0,  1.0,  1.0,

			// Back face
			-1.0, -1.0, -1.0,
			-1.0,  1.0, -1.0,
			1.0,  1.0, -1.0,
			1.0, -1.0, -1.0,

			// Top face
			-1.0,  1.0, -1.0,
			-1.0,  1.0,  1.0,
			1.0,  1.0,  1.0,
			1.0,  1.0, -1.0,

			// Bottom face
			-1.0, -1.0, -1.0,
			1.0, -1.0, -1.0,
			1.0, -1.0,  1.0,
			-1.0, -1.0,  1.0,

			// Right face
			1.0, -1.0, -1.0,
			1.0,  1.0, -1.0,
			1.0,  1.0,  1.0,
			1.0, -1.0,  1.0,

			// Left face
			-1.0, -1.0, -1.0,
			-1.0, -1.0,  1.0,
			-1.0,  1.0,  1.0,
			-1.0,  1.0, -1.0]);
	gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
	vbo.size = vertices.length / 3.0;

	// indices
	var ibo = gl.createBuffer();
	gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ibo);
	var indices = new Uint16Array([
		0, 1, 2,      0, 2, 3,    // Front face
		4, 5, 6,      4, 6, 7,    // Back face
		8, 9, 10,     8, 10, 11,  // Top face
		12, 13, 14,   12, 14, 15, // Bottom face
		16, 17, 18,   16, 18, 19, // Right face
		20, 21, 22,   20, 22, 23  // Left face
			]);
	gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indices, gl.STATIC_DRAW);
	ibo.size = indices.length;

	//normals
	var nbo = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, nbo);
	var normals = new Float32Array([
			// Front face
			0.0,  0.0,  1.0,
			0.0,  0.0,  1.0,
			0.0,  0.0,  1.0,
			0.0,  0.0,  1.0,

			// Back face
			0.0,  0.0, -1.0,
			0.0,  0.0, -1.0,
			0.0,  0.0, -1.0,
			0.0,  0.0, -1.0,

			// Top face
			0.0,  1.0,  0.0,
			0.0,  1.0,  0.0,
			0.0,  1.0,  0.0,
			0.0,  1.0,  0.0,

			// Bottom face
			0.0, -1.0,  0.0,
			0.0, -1.0,  0.0,
			0.0, -1.0,  0.0,
			0.0, -1.0,  0.0,

			// Right face
			1.0,  0.0,  0.0,
			1.0,  0.0,  0.0,
			1.0,  0.0,  0.0,
			1.0,  0.0,  0.0,

			// Left face
			-1.0,  0.0,  0.0,
			-1.0,  0.0,  0.0,
			-1.0,  0.0,  0.0,
			-1.0,  0.0,  0.0]);
        gl.bufferData(gl.ARRAY_BUFFER, normals, gl.STATIC_DRAW);
	nbo.size = normals.length / 3;

	// colors
	var cbo = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, cbo);
	var colors = new Float32Array([
			// Front face
			1.0, 1.0, 1.0, 1.0,
			1.0, 1.0, 1.0, 1.0,
			1.0, 1.0, 1.0, 1.0,
			1.0, 1.0, 1.0, 1.0,

			// Back face
			1.0, 0.0, 0.0, 1.0,
			1.0, 0.0, 0.0, 1.0,
			1.0, 0.0, 0.0, 1.0,
			1.0, 0.0, 0.0, 1.0,

			// Top face
			0.0, 1.0, 0.0, 1.0,
			0.0, 1.0, 0.0, 1.0,
			0.0, 1.0, 0.0, 1.0,
			0.0, 1.0, 0.0, 1.0,

			// Bottom face
			0.0, 0.0, 1.0, 1.0,
			0.0, 0.0, 1.0, 1.0,
			0.0, 0.0, 1.0, 1.0,
			0.0, 0.0, 1.0, 1.0,

			// Right face
			1.0, 1.0, 0.0, 1.0,
			1.0, 1.0, 0.0, 1.0,
			1.0, 1.0, 0.0, 1.0,
			1.0, 1.0, 0.0, 1.0,

			// Left face
			1.0, 0.0, 1.0, 1.0,
			1.0, 0.0, 1.0, 1.0,
			1.0, 0.0, 1.0, 1.0,
			1.0, 0.0, 1.0, 1.0]);
	gl.bufferData(gl.ARRAY_BUFFER, colors, gl.STATIC_DRAW);
	cbo.size = colors.length / 4.0;

	// model matrix
	var modelMatrix = mat4.identity();
	return [new Object(vbo, ibo, nbo, cbo, modelMatrix)];
}

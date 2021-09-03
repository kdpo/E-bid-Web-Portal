$(document).ready(function() {

	$("#btn-submit").click(function (event) {
		event.preventDefault();
		document.getElementById("overlay").style.display = "block";
		if (document.querySelector("#password").value == '') {
			$('#errorAlert').text("Please fill out all fields.").show();
			document.getElementById("overlay").style.display = "none";
			return;
		}
		encrypt();
	});

	$('#flexCheckDefault').click(function (event) {		
		if ($('#flexCheckDefault').is(':checked')) {
			$('#btn-submit').prop('disabled', false);
		} else {
			$('#btn-submit').prop('disabled', true);
		}
	});

	/*$('#btn-continue').click(function (event) {		
		$("#terms").toggle();
		$("#e-bid-form").toggle();
	});*/
});

async function zipData(string1, string2, name1, name2) {
	// use a BlobWriter to store with a ZipWriter the zip into a Blob object
	const blobWriter = new zip.BlobWriter("application/zip");
	const writer = new zip.ZipWriter(blobWriter);
	const password = $('#password').val();
	
	// use a TextReader to read the String to add
	await writer.add(name1 + ".txt", new zip.TextReader(string1), {password: password, zipCrypto: true});
	await writer.add(name2, new zip.TextReader(string2));

	// close the ZipReader
	await writer.close();

	// get the zip file as a Blob
	const blob = await blobWriter.getData();
	return blob;
}

function encrypt(){
	// get public key from api
	$.ajax({ 
		url: "/api/get_public_key/",
		success: function(res) { 
			try {
				var file = document.querySelector("#formFile").files[0];
				const public = res.public_key; 

				// read file as base64 using FileReader (reads asynchronously)
				readFile(file, function(e) {				
					var b64 = e.target.result;
					// configure options for encryption
					public_key = openpgp.key.readArmored(public).keys[0];
					const options = {
						data: b64,
						publicKeys: public_key,
						armor: true,
					};

					//generate checksum
					const shaObj = new jsSHA("SHA-256", "B64", { encoding: "UTF8" });
					shaObj.update(b64.slice(28));
					const hash = shaObj.getHash("HEX");

					var checksum = "SHA-256 CHECKSUM: " + hash + "\n" + "FILENAME: " + file.name + "\n" + "SENDER: " + $('#email').val();

					openpgp.encrypt(options).then(results => {  
						// create download link for users once submitted 
						var download_button = document.createElement("button");
						download_button.innerHTML = "Download zip file."
						download_button.className += 'btn btn-success';

						// archive files with password
						zipData(results.data, checksum, file.name, "checksum.txt").then(res => {
							//use FileSaver for downloading files
							download_button.onclick = function (event) {
								saveAs(res, file.name+".zip");
							}

							// append all info before transmitting to server.
							var data = new FormData();
							data.append("email", $('#email').val());
							data.append("bid_id", $('#bid_id').val());
							data.append("formFile", res, file.name+".zip");

							// async POST to flask route
							$.ajax({
								data : data,
								processData: false,
								contentType: false,
								type : 'POST',
								url: '/process',
								success: function(data) {
									$('#errorAlert').hide();
									swal({
										title: "Success!",
										content: download_button,
										text: "Filename: " + data.filename + '\n' + "sha256sum: " + hash + '\n' + "Time: " + data.time,
										icon: "success",
										button: "OK",
										closeOnClickOutside: false
									});
									document.getElementById("overlay").style.display = "none";
								},
								error: function(data) {
									$('#errorAlert').text(data.responseJSON['error']).show();
									document.getElementById("overlay").style.display = "none";
								}
							});

						});   		
					});
				});
			} catch (error) {
				$('#errorAlert').text("Please upload the bid document.").show();
				document.getElementById("overlay").style.display = "none";
			}	
		},
		error: function(data) {
			console.log(data);
			$('#errorAlert').text("Connection timed out. Please try again later.").show();
			document.getElementById("overlay").style.display = "none";
		}
	});
}

function readFile(file, callback){
    var reader = new FileReader();
    reader.onload = callback
    reader.readAsDataURL(file);
}
document.querySelector("#decrypt").addEventListener('click', function() {
	document.getElementById("overlay").style.display = "block";
	$('#errorAlert').hide();
	$('#successAlert').hide();
	
	// no file selected to read
	if(document.querySelector("#file").value == '' || document.querySelector("#pkey").value == '') {
		$('#errorAlert').text('Please provide all necessary files.').show();
		document.getElementById("overlay").style.display = "none";
		return;
	}

	var file = document.querySelector("#file").files[0];
	var pkey = document.querySelector("#pkey").files[0];

	var reader = new FileReader();

	reader.onload = (function(f) {
		return function(e) {
	        privateArmoredKey = e.target.result;
	        
	        var zipreader = new FileReader();
	        zipreader.onload = (function(f) {
	        	
	        	return function(e) {
	        		dataURI = e.target.result;
	        		readZip(dataURI, $('#password').val()).then( fileData => {
	        			if (!fileData) {
	        				$('#errorAlert').text('Invalid AES password.').show();
	        				document.getElementById("overlay").style.display = "none";
	        			} else {
	        				const encrypted = fileData;
	        				var passphrase = $('#passphrase').val();
	        				var message, privateKey;

	        				(async () => {			
	        					try{
	        						privateKey = await openpgp.decryptKey({
	        							privateKey: await openpgp.readPrivateKey({ armoredKey: privateArmoredKey }),
	        							passphrase
	        						});

	        						message = await openpgp.readMessage({
	        					   	 armoredMessage: encrypted // parse armored message
	        						});

	        						const { data: decrypted, signatures } = await openpgp.decrypt({
	        							message,
	        						    decryptionKeys: privateKey
	        						});

	        						var b64 = decrypted.slice(28);
	        						
	        						var bin = atob(b64);
	        						// Display file size
	        						console.log('File Size:', Math.round(bin.length / 1024), 'KB');
	        						console.log('PDF Version:', bin.match(/^.PDF-([0-9.]+)/)[1]);

	        						// Insert a link that allows the user to download the PDF file
	        						$('#download-button').prop('disabled', false);
	        						var download = document.getElementById("download");
	        						download.download = file.name.replace(".zip", "");
	        						download.href='data:application/octet-stream;base64,' + b64;   
	        						$('#successAlert').text('Successfully decrypted!').show();  
	        						document.getElementById("overlay").style.display = "none";

	        					} catch (error) {
	        						console.log(error.name);
	        						$('#errorAlert').text(error.message).show();
	        						document.getElementById("overlay").style.display = "none";	
	        					}	
	        							
	        				})();
	        			}
	        		});
	        	};

	        })(file);

	        zipreader.readAsDataURL(file);
	    };
	})(pkey);

	reader.readAsText(pkey);
});

async function readZip (dataURI, password) {
	const zipReader = new zip.ZipReader(new zip.Data64URIReader(dataURI), { password: password });
	try{
		// - get entries from the zip file
		const entries = await zipReader.getEntries();
		
		const data = await entries[0].getData(new zip.TextWriter()).catch(e => console.log('Error: ', e.message));
		return data;
	} catch (error) {
		if (error.message === zip.ERR_ENCRYPTED ||
		        error.message === zip.ERR_INVALID_PASSWORD) {
			console.log(error.message);
		} else {
		    throw error;
		}
		return null;
	} finally {
		await zipReader.close();
	}
}
// provide BucketName, bucketRegion, and IdentityPoolId 
// see https://aws.amazon.com/s3/ for documentation
var BucketName = '';
var bucketRegion = '';
var IdentityPoolId = '';

AWS.config.update({
  region: bucketRegion,
  credentials: new AWS.CognitoIdentityCredentials({
    IdentityPoolId: IdentityPoolId
  })
});

var s3 = new AWS.S3({
  apiVersion: "2006-03-01",
  params: { Bucket: BucketName }
});


function my_upload(folder) {
    
    if ((BucketName == '') || (bucketRegion == '') || (IdentityPoolId = ''))        
        return alert("Please set correct BucketName, bucketRegion, and IdentityPoolId in html/upload.js")
    
    var files = document.getElementById("upload").files

    //   var files = window.my_file
    if (!files.length) 
        return alert("Please choose a file to upload first.")
    
    var file = files[0]

    console.log('uploading...') 

    console.log('file', file) 

    var fileName = file.name
    var folderKey = encodeURIComponent(folder) + "/"

    var fileKey = folderKey + fileName

    // Use S3 ManagedUpload class as it supports multipart uploads
    var upload = new AWS.S3.ManagedUpload({
    params: {
      Bucket: BucketName,
      Key: fileKey,
      Body: file
    }
    })

    var email = document.getElementById("exampleInputEmail1").value 
    var citation = document.getElementById("citation").value 
    var comments = document.getElementById("exampleFormControlTextarea1").value

    var info = "email: " + email + '\ncitation: ' + citation + '\ncomments: ' + comments 

    var info_file = new File([info], fileName + "_info.txt", {
      type: "text/plain",
    });  

    var info_fileKey = folderKey + info_file.name;  

    // Use S3 ManagedUpload class as it supports multipart uploads
    var info_upload = new AWS.S3.ManagedUpload({
    params: {
      Bucket: BucketName,
      Key: info_fileKey,
      Body: info_file
    }
    });  

    console.log('email', email)    

    var promise = upload.promise();

    promise.then(
    function (data) {
      alert("Successfully uploaded file.");
    },
    function (err) {
      return alert("There was an error uploading your file: ", err.message);
    }
    );

    var info_promise = info_upload.promise();

    info_promise.then(
    function (data) {
      console.log('info upload success')
    },
    function (err) {
      return alert("There was an error uploading your file: ", err.message);
    }
    );  
    
  
    
//     var file = new File(["foo"], "foo.txt", {
//       type: "text/plain",
//     });
}


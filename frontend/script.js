const API_BASE = ""; 

// Send query to /ask endpoint
async function sendQuery() {
 const query = document.getElementById("queryInput").value;
 if (!query) return alert("Please enter a query!");

 // We use 'API_BASE' + '/ask' which resolves to just '/ask'
 const res = await fetch(`${API_BASE}/ask?query=${encodeURIComponent(query)}`, {
  method: "POST"
 });

 const data = await res.json();
 document.getElementById("responseOutput").innerText = data.response;
 document.getElementById("logsOutput").innerText = JSON.stringify(data.logs, null, 2);
}

// Upload PDF to /upload_pdf
async function uploadPDF() {
 const fileInput = document.getElementById("pdfUpload");
 if (fileInput.files.length === 0) return alert("Please select a PDF!");

 const formData = new FormData();
 formData.append("file", fileInput.files[0]);

 // We use 'API_BASE' + '/upload_pdf' which resolves to just '/upload_pdf'
 const res = await fetch(`${API_BASE}/upload_pdf`, {
  method: "POST",
  body: formData
 });

 const data = await res.json();
 alert(data.status || "PDF uploaded!");
}
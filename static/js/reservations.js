
document.getElementById('paymentForm').addEventListener('submit', function (event) {
    var cardNumber = document.getElementById('cardNumber').value;
    // Simple check to see if the card number contains 16 digits
    if (!/^\d{16}$/.test(cardNumber.replace(/\s/g, ''))) {
        alert("Please enter a valid 16-digit card number.");
        event.preventDefault(); // Prevent form from submitting
    }
});

// Get the modal
var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal 
btn.onclick = function () {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function () {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

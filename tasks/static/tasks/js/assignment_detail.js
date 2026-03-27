const input = document.getElementById("chatInput");
const typing = document.getElementById("typing");
const chat = document.getElementById("chatMessages");
const form = document.querySelector(".chat-input");

// =====================
// AUTO SCROLL (LOAD)
// =====================
window.onload = () => {
setTimeout(() => {
chat.scrollTop = chat.scrollHeight;
}, 100);
};

// =====================
// TYPING INDICATOR
// =====================
input.addEventListener("input", () => {
typing.style.display = input.value ? "block" : "none";
});

// =====================
// ENTER LOGIC
// =====================
input.addEventListener("keypress", function(e){

```
if(e.key === "Enter"){
    e.preventDefault();

    let value = input.value.trim();

    if(value.length === 0){
        const approveBtn = document.querySelector("button[value='approve']");
        if(approveBtn) approveBtn.click();
    }else{
        document.querySelector("button[value='auto']").click();
    }
}
```

});

// =====================
// AUTO SCROLL (SUBMIT)
// =====================
form.addEventListener("submit", () => {
setTimeout(() => {
chat.scrollTop = chat.scrollHeight;
}, 50);
});



function checkDigit(){
    id=document.getElementById('course').value;
    console.log("here")
    if (id.length!=3)
        confirm("Course ID "+id+" is invlid, it can be only 3 digits.")


}

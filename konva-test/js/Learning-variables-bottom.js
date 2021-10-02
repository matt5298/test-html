myBottomVar = "Bottom Text";

console.log('loading bottom Script!')

function bottomScript(){
    this.getText = function(){
        return "This is from the bottom!";
    }

    this.setText = function(){
        div = document.getElementById('t1');
        para = document.createElement('p');
        //this doesn't happen
        para.textContent = 'This text is inserted when the javascript file is executed on loading it into web page, the function has n0t even been called';
        div.appendChild(para);
        console.log('loaded bottomScript.setText()')
    }

    this.myMethod = () => {
        console.log('What is happening now?');
    }
};

        div3 = document.getElementById('t1');
        para = document.createElement('p');
        //this doesn't happen
        para.textContent = 'This text is inserted when the javascript file is executed on loading, it is outside the function';
        div3.appendChild(para);
        console.log('at the bottom of bottom script when loaded')


pragma solidity >= 0.8.11 <= 0.8.11;

contract CrowdFunding {
    string public newuser;
    string public transaction;
    string public linkaccount;
       
    //call this function to save new user data to Blockchain
    function signup(string memory nu) public {
       newuser = nu;	
    }
   //get user details
    function getUser() public view returns (string memory) {
        return newuser;
    }

    function setTransaction(string memory t) public {
       transaction = t;	
    }

    function getTransaction() public view returns (string memory) {
        return transaction;
    }

    function setLinkaccount(string memory la) public {
       linkaccount = la;	
    }

    function getLinkaccount() public view returns (string memory) {
        return linkaccount;
    }

    constructor() public {
        transaction = "";
	linkaccount="";
	newuser="";
    }
}
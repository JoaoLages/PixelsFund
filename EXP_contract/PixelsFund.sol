pragma solidity ^0.4.15;
import "./SafeMath.sol";
import "./HumanStandardToken.sol";

contract PixelsFund{
    using SafeMath for uint;
    
    mapping (address => uint) public investments;
    
    uint public total_invested = 0;
    
    address public owner;
    bool public still_going  = true;
    address[] private addresses;
    address[] private projects;
    
    HumanStandardToken private exposure;
    
    uint private final_total = 0;
    
    modifier onlyOwner { 
        require(msg.sender == owner);
        _;
    }
    
    function PixelsFund() {
        owner = msg.sender;
    }
    
    function invest(address project, uint amount) onlyOwner {
        projects.push(project);
        exposure.transfer(project, amount);
    }
    
    function check_if_is_project(address adr) private returns(bool) {
        for(uint i=0; i<projects.length; i++)
            if(projects[i] == adr)
                return true;
        return false;
    }
    
    function instatiate_exposure(address adr) onlyOwner {
        exposure = HumanStandardToken(adr);
    }

    function has_index(address investor) private returns(bool) {
        for (uint i=0; i<addresses.length; i++){
            if (addresses[i] == investor)
                return true;
        }
        return false;
    }
    
    function transfer_to_investor(address investor, uint amount) private returns(bool){
        return exposure.transfer(investor, amount);
    }

    function onDeposit(address depositor, uint amount) onlyOwner {
        
        //if depositor is not a project, it is an investor
        if (check_if_is_project(depositor) != true && still_going){
            
            if (has_index(depositor) == false)
                addresses.push(depositor);
            
            investments[depositor] += amount;
            total_invested += amount;
            
        //if depositor is a project, share dividends
        } else {
            still_going = false;
            uint invested;
            uint due;
            for(uint i=0; i<addresses.length; i++){
                invested = investments[addresses[i]];
                due = invested.mul(amount).mul(7).div(uint(10).mul(total_invested));
                transfer_to_investor(addresses[i], due);
            }
        }
    }
}
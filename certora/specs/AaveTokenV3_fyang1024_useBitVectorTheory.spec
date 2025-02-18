import "./AaveTokenV3_fyang1024.spec"

/*
    @Rule

    @Description:
        If a user has not delegated to anyone and now delegate,
        it should decrease self power but increase delegatee power by its balance, while not affecting other's power.

    @Note:
        This rule needs to be run with --settings -useBitVectorTheory flag, but the server threw
        [java.lang.IllegalStateException: max size of bit vector 256 literals exceeded by 
        115792089237316195423570985008687907853269984665640564039457584007913129639936],
        hence this rule has not been verified yet.
*/
rule delegate_affects_self_and_delegatee_only(address delegatee, uint8 delegationType, address other) {
    env e;
    address self = e.msg.sender;
    require self != other && self != delegatee && delegatee != other && delegatee != 0;
    require delegationType == VOTING_POWER() || delegationType == PROPOSITION_POWER();
    if (delegationType == VOTING_POWER()) {
        require !getDelegatingVoting(self);
    } else {
        require !getDelegatingProposition(self);
    }
    require getDelegateeByType(self, delegationType) == 0; // not delegating now

    uint256 selfBalance = balanceOf(self);
    uint256 _selfPower = getPowerCurrent(self, delegationType);
    uint256 _delegateePower = getPowerCurrent(delegatee, delegationType);
    uint256 _otherPower = getPowerCurrent(other, delegationType);

    require selfBalance < MAX_DELEGATED_BALANCE();
    require _selfPower < MAX_DELEGATED_BALANCE();
    require _delegateePower < MAX_DELEGATED_BALANCE();
    require _selfPower >= selfBalance;

    delegateByType(e, delegatee, delegationType);

    uint256 selfPower_ = getPowerCurrent(self, delegationType);
    uint256 delegateePower_ = getPowerCurrent(delegatee, delegationType);
    uint256 otherPower_ = getPowerCurrent(other, delegationType);

    assert getDelegateeByType(self, delegationType) == delegatee;
    assert _selfPower - selfBalance == selfPower_; // selfPower decreased by selfBalance
    assert _delegateePower + normalize(selfBalance) == delegateePower_; // delegateePower increased by selfBalance
    assert _otherPower == otherPower_; // otherPower does not change
}

/*
    @Rule

    @Description:
        If a user has delegated to someone and now undelegates (delegates to self),
        it should increase self power but decrease delegatee power, while not affecting other power.

    @Note:
        This rule needs to be run with --settings -useBitVectorTheory flag, but the server threw
        [java.lang.IllegalStateException: max size of bit vector 256 literals exceeded by 
        115792089237316195423570985008687907853269984665640564039457584007913129639936],
        hence this rule has not been verified yet.
*/
rule undelegate_affects_self_and_delegatee_only(uint8 delegationType, address other) {
    env e;
    address self = e.msg.sender;
    require self != other;
    require delegationType == VOTING_POWER() || delegationType == PROPOSITION_POWER();

    if (delegationType == VOTING_POWER()) {
        require getDelegatingVoting(self);
    } else {
        require getDelegatingProposition(self);
    }
    address delegatee = getDelegateeByType(self, delegationType);
    require delegatee != other && delegatee != self && delegatee != 0;

    uint256 selfBalance = balanceOf(self);
    uint256 _selfPower = getPowerCurrent(self, delegationType);
    uint256 _delegateePower = getPowerCurrent(delegatee, delegationType);
    uint256 _otherPower = getPowerCurrent(other, delegationType);

    require selfBalance < MAX_DELEGATED_BALANCE();
    require _selfPower < MAX_DELEGATED_BALANCE();
    require _delegateePower < MAX_DELEGATED_BALANCE();
    require _delegateePower >= selfBalance;

    delegateByType(e, self, delegationType); // undelegate

    uint256 selfPower_ = getPowerCurrent(self, delegationType);
    uint256 delegateePower_ = getPowerCurrent(delegatee, delegationType);
    uint256 otherPower_ = getPowerCurrent(other, delegationType);

    assert getDelegateeByType(self, delegationType) == 0; // no delegatee anymore
    assert _selfPower + selfBalance == selfPower_; // selfPower increased by selfBalance
    assert _delegateePower - normalize(selfBalance) == delegateePower_; // delegateePower decreased by selfBalance
    assert _otherPower == otherPower_; // otherPower does not change
}

/*
    @Rule

    @Description:
        delegation of voting power should not affect proposition power, and vice versa.
    
    @Note:
        This rule needs to be run with --settings -useBitVectorTheory flag, but the server threw
        [java.lang.IllegalStateException: max size of bit vector 256 literals exceeded by 
        115792089237316195423570985008687907853269984665640564039457584007913129639936],
        hence this rule has not been verified yet.
*/
rule independency_of_delegation_types(uint8 delegationType) {
    env e;
    address self = e.msg.sender;
    address other;
    require other != 0 && other != self;
    require delegationType == VOTING_POWER() || delegationType == PROPOSITION_POWER();

    uint8 otherDelegationType;
    if (delegationType == VOTING_POWER()) {
        otherDelegationType = PROPOSITION_POWER();
    } else {
        otherDelegationType = VOTING_POWER();
    }

    uint256 _selfPower = getPowerCurrent(self, otherDelegationType);
    uint256 _otherPower = getPowerCurrent(other, otherDelegationType);
    address _delegatee;
    if (otherDelegationType == VOTING_POWER()) {
        _delegatee = getVotingDelegate(self);
    } else {
        _delegatee = getPropositionDelegate(self);
    }
    bool _delegating;
    if (otherDelegationType == VOTING_POWER()) {
        _delegating = getDelegatingVoting(self);
    } else {
        _delegating = getDelegatingProposition(self);
    }

    delegateByType(e, other, delegationType);

    uint256 selfPower_ = getPowerCurrent(self, otherDelegationType);
    uint256 otherPower_ = getPowerCurrent(other, otherDelegationType);
    address delegatee_;
    if (otherDelegationType == VOTING_POWER()) {
        delegatee_ = getVotingDelegate(self);
    } else {
        delegatee_ = getPropositionDelegate(self);
    }
    bool delegating_;
    if (otherDelegationType == VOTING_POWER()) {
        delegating_ = getDelegatingVoting(self);
    } else {
        delegating_ = getDelegatingProposition(self);
    }

    assert _selfPower == selfPower_;
    assert _otherPower == otherPower_;
    assert _delegatee == delegatee_;
    assert _delegating == delegating_;
}
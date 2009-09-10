
"""
Test the creation and data handling of policies.
"""

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import Policy, ForbiddenError, UserRequiredError, create_policy_check

import py.test

jeremy_info = {'name':'jeremy'}
chris_info = {'name':'chris','roles':['ADMIN']}
roller_info = {'name':'chris','roles':['ROLLER']}
none_info = {'name':'NONE'}
barnabas_info = {'name':'barnabas'}
randomer_info = {'name':'randomer'}
boom_info = {'name':'boom'}
guest_info = {'name':'GUEST'}

def setup_module(module):
    module.environ = {
        'tiddlyweb.config': {
            'server_host': {
                'scheme': 'http'
            }
        }
    }
    pass

def test_policy_create():
    policy = Policy()

    assert type(policy) == Policy
    assert policy.read == []
    assert policy.write == []
    assert policy.create == []
    assert policy.delete == []
    assert policy.manage == []

def test_policy_init_set():
    policy = Policy(read=['chris','jeremy'],write=['NONE'],manage=['chris'])

    assert policy.read == ['chris','jeremy']
    assert policy.write == ['NONE']
    assert policy.create == []
    assert policy.delete == []
    assert policy.manage == ['chris']

def test_policy_post_set():
    policy = Policy(read=['chris','jeremy'],write=['NONE'],manage=['chris'])

    assert policy.read == ['chris','jeremy']

    policy.read = ['one','tall']

    assert 'chris' not in policy.read
    assert 'jeremy' not in policy.read
    assert 'tall' in policy.read

def test_policy_allows():
    policy = Policy(read=['chris','jeremy'],write=['NONE'],delete=['R:ADMIN'],manage=['chris'])

    assert policy.allows(chris_info, 'read', environ)
    assert policy.allows(chris_info, 'delete', environ)
    assert policy.allows(jeremy_info, 'read', environ)
    py.test.raises(ForbiddenError, 'policy.allows(jeremy_info, "write", environ)')
    assert policy.allows(chris_info, 'manage', environ)
    py.test.raises(ForbiddenError, 'policy.allows(jeremy_info, "manage", environ)')
    assert policy.allows(chris_info, 'create', environ)
    py.test.raises(ForbiddenError, 'policy.allows(none_info, "write", environ)')
    py.test.raises(ForbiddenError, 'policy.allows(barnabas_info, "read", environ)')
    py.test.raises(ForbiddenError, 'policy.allows(barnabas_info, "write", environ)')
    assert policy.allows(barnabas_info, 'create', environ)
    py.test.raises(ForbiddenError, 'policy.allows(barnabas_info, "manage", environ)')

def test_policy_any():
    policy = Policy(read=['ANY'],write=['ANY'])
    assert policy.allows(randomer_info, 'read', environ)
    assert policy.allows(boom_info, 'write', environ)
    py.test.raises(UserRequiredError, 'policy.allows(guest_info, "read", environ)')

def test_bag_policy():

    bag = Bag('policy_tester')
    bag.policy = Policy(read=['chris','jeremy'])

    assert bag.policy.allows(chris_info, 'read', environ)
    py.test.raises(UserRequiredError, 'bag.policy.allows(guest_info, "read", environ)')

def test_user_perms():
    policy = Policy()
    assert policy.user_perms(chris_info) == ['read','write','create','delete']

    policy = Policy(read=['R:ADMIN'], write=['R:ADMIN'], create=['jeremy'], delete=['jeremy'])
    assert policy.user_perms(chris_info) == ['read','write']

    assert policy.user_perms(jeremy_info) == ['create', 'delete']

def test_create_policy_check():
    no_environ = {'tiddlyweb.config':{'bag_create_policy':''}}
    all_environ = {'tiddlyweb.config':{'recipe_create_policy':''}}
    any_environ = {'tiddlyweb.config':{'recipe_create_policy':'ANY'}}
    admin_environ = {'tiddlyweb.config':{'recipe_create_policy':'ADMIN'}}
    weird_environ = {'tiddlyweb.config':{'recipe_create_policy':'WEIRD'}}

    py.test.raises(ForbiddenError, 'create_policy_check(no_environ, "recipe", chris_info)')
    assert create_policy_check(all_environ, "recipe", chris_info)
    assert create_policy_check(any_environ, "recipe", chris_info)
    py.test.raises(UserRequiredError, 'create_policy_check(any_environ, "recipe", {"name":"GUEST"})')
    assert create_policy_check(admin_environ, "recipe", chris_info)
    py.test.raises(ForbiddenError, 'create_policy_check(admin_environ, "recipe", jeremy_info)')
    py.test.raises(ForbiddenError, 'create_policy_check(admin_environ, "recipe", roller_info)')
    py.test.raises(ForbiddenError, 'create_policy_check(weird_environ, "recipe", jeremy_info)')

def test_malformed_policy():
    policy = Policy()
    policy.read = None # set the policy to a bad form
    assert policy.allows(guest_info, 'read', environ)

def test_confirm_attributes():
    """Confirm the class attributes of a policy."""
    attributes = Policy.attributes
    for name in ['read', 'write', 'create', 'delete', 'accept', 'manage', 'owner']:
        assert name in attributes


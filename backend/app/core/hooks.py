"""Extension points.

A module can plug extra behaviour into another module by adding a function to one of these lists,
without editing the other module's files. This is why three people can work in the same module
and never touch the same file.

  login_before   functions(user_or_None)   run before the password is checked (may raise HTTPException)
  login_failed   functions(db, user)       run after a wrong password for an existing account
  login_success  functions(db, user)       run after a correct password
  post_scan      functions(scan, findings) run when all checks have finished
"""
from typing import Callable

login_before: list[Callable] = []
login_failed: list[Callable] = []
login_success: list[Callable] = []
post_scan: list[Callable] = []

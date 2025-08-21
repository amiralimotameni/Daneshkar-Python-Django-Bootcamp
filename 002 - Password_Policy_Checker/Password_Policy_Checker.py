# >>>>> Inputs <<<<<
username = input("Enter your username: ").strip()
password = input("Enter your password: ").strip()

# >>>>> Top Score Variable & Failed Parameters <<<<<
top_score = 7
score = top_score
failed_parameters = []
print("\n")

# >>>>> length Checker <<<<<
if len(password) <= 8:
    score -= 1
    failed_parameters.append("Password must be longer than 8 characters.")

# >>>>> List of Special Letters <<<<<
specials = ['!', '@', '$', '?']

# >>>>> Special Letters Checker <<<<<
check_special = False
for character in password:
    if character in specials:
        check_special = True
        break

# >>>>> Letter Checker <<<<<
check_letter = False
for character in password:
    if ('a' <= character <= 'z') or ('A' <= character <= 'Z'):
        check_letter = True
        break

# >>>>> Combine: must have at least one letter AND one special <<<<<
if not (check_letter and check_special):
    score -= 1
    failed_parameters.append("Password Failed: At least one letter and one special character must be present.")

# >>>>> Not equal to username Checker <<<<<
if password == username:
    score -= 1
    failed_parameters.append("Password cannot be the same as username.")


# >>>>> Case Checker <<<<<
check_lower = False
check_upper = False
for character in password:
    if 'a' <= character <= 'z':
        check_lower = True
    elif 'A' <= character <= 'Z':
        check_upper = True

# >>>>> All-lowercase or All-uppercase <<<<<
if (check_lower or check_upper) and not (check_lower and check_upper):
    score -= 1
    failed_parameters.append("Password cannot be all-lowercase or all-uppercase.")

# >>>>> Swapcase of username Checker <<<<<
if (password != username) and (password == username.swapcase()):
    score -= 1
    failed_parameters.append("Password is swapcase version of username.")

# >>>>> Symbol-replacement (use ChatGPT)  <<<<<
u_low = username.lower()
p_low = password.lower()

t_i = str.maketrans({'@': 'a', '$': 's', '!': 'i', '0': 'o'})
t_l = str.maketrans({'@': 'a', '$': 's', '!': 'l', '0': 'o'})

p_norm_i = p_low.translate(t_i)
p_norm_l = p_low.translate(t_l)

used_symbols = any(c in '@$!0' for c in password)
if used_symbols and (p_norm_i == u_low or p_norm_l == u_low):
    score -= 1
    failed_parameters.append("Password contains symbols replacing letters (e.g. '@' for 'a').")

# >>>>> Part 7 — Common or "password"-like use Chat GPT <<<<<
common_pw = {
    "123456","12345678","123456789","12345","111111",
    "qwerty","asdfgh","zxcvbnm","password","admin"
}

pw_low = password.lower()
if pw_low in common_pw:
    score -= 1
    failed_parameters.append("Password is too common or similar to 'password'.")
else:
    t_pw = str.maketrans({'@':'a', '$':'s', '0':'o'})
    pw_norm = pw_low.translate(t_pw)
    pw_norm_alnum = "".join(ch for ch in pw_norm if ch.isalnum())
    if pw_norm_alnum == "password":
        score -= 1
        failed_parameters.append("Password is too common or similar to 'password'.")

# >>>>> Output <<<<<
print(f"Password Strength: {score}/{top_score}")
level = "Weak"
if score >= 5:
    level = "Strong"
elif score >= 3:
    level = "Medium"
print(f"Level: {level}")
print("Failed Checks:")
for reason in failed_parameters:
    print(f"- {reason}")

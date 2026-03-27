(function(){
  const form = document.getElementById('loginForm');
  const username = document.getElementById('username');
  const password = document.getElementById('password');
  const roleRadios = document.getElementsByName('role');
  const remember = document.getElementById('remember');
  const error = document.getElementById('error');
  const toggle = document.getElementById('togglePwd');

  toggle.addEventListener('click', ()=>{
    if(password.type === 'password'){
      password.type = 'text';
      toggle.textContent = 'Hide';
    } else {
      password.type = 'password';
      toggle.textContent = 'Show';
    }
  });

  form.addEventListener('submit', (e)=>{
    e.preventDefault();
    error.textContent = '';
    const em = username.value.trim();
    const pw = password.value;
    let rl = 'Student';
    for(const r of roleRadios){ if(r.checked){ rl = r.value; break; } }

    if(!em){ error.textContent = 'Please enter a username.'; username.focus(); return; }
    // If student, enforce a USN-like format (basic check: alphanumeric, min length 6)
    if(rl === 'Student'){
      const usnPattern = /^[0-9A-Za-z]{6,20}$/;
      if(!usnPattern.test(em)){
        error.textContent = 'For students use your USN (e.g. 1PV16CS001).';
        username.focus();
        return;
      }
    } else {
      if(em.length < 3){ error.textContent = 'Username must be at least 3 characters.'; username.focus(); return; }
    }

    if(pw.length < 4){ error.textContent = 'Password must be at least 4 characters.'; password.focus(); return; }

    // Mock authentication: accept any credentials for demo
    const auth = { username: em, role: rl, time: Date.now() };
    try{
      localStorage.setItem('college_auth', JSON.stringify(auth));
    }catch(_){ /* ignore storage errors */ }

    // Redirect to simple dashboard
    const params = new URLSearchParams();
    params.set('role', rl);
    window.location.href = 'dashboard.html?' + params.toString();
  });
})();

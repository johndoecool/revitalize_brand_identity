"""
Mock HTML responses for testing

Contains realistic mock HTML responses for different websites and platforms.
"""

# Facebook mock responses
FACEBOOK_SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Microsoft - Home | Facebook</title>
    <meta name="description" content="Microsoft company page on Facebook">
</head>
<body>
    <div id="facebook-root" role="main">
        <h1>Microsoft</h1>
        <div aria-label="18,234,567 people like this page">18,234,567 people like this</div>
        <div aria-label="18.2M followers">18.2M followers</div>
        
        <!-- Posts -->
        <div data-testid="post_message" class="userContent">
            <p>We're excited to announce our new AI-powered productivity tools! 
            These innovations will help you work smarter and more efficiently. 
            #Innovation #AI #Productivity</p>
        </div>
        <div data-testid="post_message" class="userContent">
            <p>Thank you to all our amazing customers for your continued support! 
            Your feedback drives our innovation. #CustomerFirst #Technology</p>
        </div>
        <div data-testid="post_message" class="userContent">
            <p>Join us at the upcoming tech conference where we'll showcase 
            our latest cloud computing solutions. #Cloud #TechConference</p>
        </div>
    </div>
</body>
</html>
"""

FACEBOOK_LOGIN_REDIRECT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook - Log In or Sign Up</title>
</head>
<body>
    <div class="fb_content">
        <h1>Log in to Facebook</h1>
        <p>You must log in to continue.</p>
        <form action="/login.php" method="post">
            <input type="text" name="email" placeholder="Email address or phone number">
            <input type="password" name="pass" placeholder="Password">
            <button type="submit">Log In</button>
        </form>
    </div>
</body>
</html>
"""

# LinkedIn mock responses
LINKEDIN_SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Microsoft | LinkedIn</title>
    <meta name="description" content="Microsoft official LinkedIn company page">
</head>
<body>
    <main>
        <div class="org-top-card">
            <h1 class="org-top-card-summary__title">Microsoft Corporation</h1>
            <div class="org-top-card-summary__follower-count">18,509,628 followers</div>
            <div class="org-top-card-summary-info-list">
                <div>Computer Software • Redmond, Washington</div>
                <div>271,000+ employees</div>
            </div>
        </div>
        
        <!-- Company posts -->
        <div class="feed-shared-update-v2">
            <div class="feed-shared-text">
                We're hiring talented engineers to join our cloud computing team! 
                If you're passionate about scalable systems and innovation, 
                we'd love to hear from you. #Hiring #CloudComputing #Engineering
            </div>
        </div>
        <div class="feed-shared-update-v2">
            <div class="feed-shared-text">
                Proud to announce our commitment to carbon neutrality by 2030. 
                Technology companies have a responsibility to lead on climate action. 
                #Sustainability #ClimateAction #CarbonNeutral
            </div>
        </div>
        <div class="feed-shared-update-v2">
            <div class="feed-shared-text">
                Our latest research in quantum computing shows promising results 
                for solving complex optimization problems. Excited about the future! 
                #QuantumComputing #Research #Innovation
            </div>
        </div>
    </main>
</body>
</html>
"""

LINKEDIN_CHALLENGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Security Challenge | LinkedIn</title>
</head>
<body>
    <div class="challenge-page">
        <h1>Security check</h1>
        <p>We need to verify that you're a real person.</p>
        <div id="authwall-join-form">
            <button class="authwall-join-form__form-toggle--bottom">Continue</button>
        </div>
    </div>
</body>
</html>
"""

# Twitter/X mock responses
TWITTER_SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Microsoft (@microsoft) / X</title>
    <meta name="description" content="Official Microsoft Twitter account">
</head>
<body>
    <main>
        <div class="profile-header">
            <div data-testid="UserName">Microsoft</div>
            <div data-testid="UserFollowers">
                <span>4.2M</span> <span>Followers</span>
            </div>
        </div>
        
        <!-- Tweets -->
        <article data-testid="tweet">
            <div data-testid="tweetText">
                🚀 Excited to announce our new AI features in Microsoft 365! 
                These tools will revolutionize how you work and collaborate. 
                Try them out today! #AI #Microsoft365 #Innovation
            </div>
        </article>
        <article data-testid="tweet">
            <div data-testid="tweetText">
                Thank you to our incredible developer community! 💙 
                Your creativity and passion drive technology forward. 
                Keep building amazing things! #Developers #Community #Tech
            </div>
        </article>
        <article data-testid="tweet">
            <div data-testid="tweetText">
                Join us at #MSBuild2024 for the latest in cloud computing, 
                AI, and developer tools. Register now: link.ms/build 
                #MSBuild #Cloud #AI #DevTools
            </div>
        </article>
    </main>
</body>
</html>
"""

# Generic website responses
GENERIC_SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Sample News Article - Tech Today</title>
    <meta name="description" content="Latest technology news and updates">
    <meta name="author" content="John Smith">
</head>
<body>
    <header>
        <h1 class="headline">Major Tech Company Announces Innovation</h1>
        <div class="byline">By <span rel="author">John Smith</span></div>
        <time datetime="2024-01-15" class="publish-date">January 15, 2024</time>
    </header>
    
    <article class="article-content">
        <p>In a major announcement today, Microsoft revealed their latest 
        innovation in artificial intelligence and cloud computing. The company 
        demonstrated remarkable progress in machine learning capabilities.</p>
        
        <p>Industry experts are praising the development as a significant 
        step forward for enterprise technology. The new features are expected 
        to improve productivity across various industries.</p>
        
        <p>Microsoft's commitment to innovation continues to position them 
        as a leader in the technology sector. Their focus on AI and cloud 
        services addresses growing market demands.</p>
    </article>
    
    <nav>
        <a href="/tech">Technology</a>
        <a href="/business">Business</a>
        <a href="/innovation">Innovation</a>
    </nav>
</body>
</html>
"""

GENERIC_404_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Page Not Found - 404</title>
</head>
<body>
    <div class="error-page">
        <h1>404 - Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
        <a href="/">Go to homepage</a>
    </div>
</body>
</html>
"""

# Error responses
FORBIDDEN_403_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Access Forbidden - 403</title>
</head>
<body>
    <div class="error-page">
        <h1>403 - Forbidden</h1>
        <p>You don't have permission to access this resource.</p>
    </div>
</body>
</html>
"""

RATE_LIMITED_429_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Too Many Requests - 429</title>
</head>
<body>
    <div class="error-page">
        <h1>429 - Too Many Requests</h1>
        <p>Rate limit exceeded. Please try again later.</p>
    </div>
</body>
</html>
"""

# Mobile-specific responses
FACEBOOK_MOBILE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Microsoft - m.facebook.com</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <div id="mobile-page">
        <h2>Microsoft</h2>
        <div class="like-count">5.2M people like this</div>
        <div class="mobile-post">Great new product announcement!</div>
        <div class="mobile-post">Thanks for your continued support</div>
    </div>
</body>
</html>
"""

# Mock response mapping for easy test access
MOCK_RESPONSES = {
    'facebook_success': FACEBOOK_SUCCESS_HTML,
    'facebook_login': FACEBOOK_LOGIN_REDIRECT_HTML,
    'facebook_mobile': FACEBOOK_MOBILE_HTML,
    'linkedin_success': LINKEDIN_SUCCESS_HTML,
    'linkedin_challenge': LINKEDIN_CHALLENGE_HTML,
    'twitter_success': TWITTER_SUCCESS_HTML,
    'generic_success': GENERIC_SUCCESS_HTML,
    'generic_404': GENERIC_404_HTML,
    'forbidden_403': FORBIDDEN_403_HTML,
    'rate_limited_429': RATE_LIMITED_429_HTML
} 
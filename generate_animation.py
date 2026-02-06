#!/usr/bin/env python3
"""
Generate a space shooter animation SVG from GitHub contributions.
The animation shows enemies (contribution days) that get shot down by a player ship.
"""

import os
import random
import requests
import json
from datetime import datetime, timedelta

def fetch_github_contributions(username, token):
    """Fetch GitHub contributions using the GraphQL API."""
    url = 'https://api.github.com/graphql'
    headers = {'Authorization': f'Bearer {token}'}
    
    # GraphQL query to fetch contributions
    query = """
    query($userName:String!) {
      user(login: $userName) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    
    variables = {'userName': username}
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data['data']['user']['contributionsCollection']['contributionCalendar']
    else:
        print(f"Failed to fetch contributions: {response.status_code}")
        return None

def generate_space_shooter_svg(contributions_data, output_file='space-shooter.svg'):
    """Generate an SVG animation showing a space shooter game based on contributions."""
    
    if not contributions_data:
        print("No contributions data available")
        return
    
    total_contributions = contributions_data['totalContributions']
    weeks = contributions_data['weeks']
    
    # Flatten contribution days
    days = []
    for week in weeks:
        days.extend(week['contributionDays'])
    
    # Take last 52 weeks of data (364 days)
    days = days[-364:] if len(days) > 364 else days
    
    # SVG dimensions
    width = 800
    height = 400
    
    # Generate enemies based on contributions
    enemies = []
    player_x = width // 2
    player_y = height - 50
    
    for i, day in enumerate(days[-30:]):  # Last 30 days for animation
        count = day['contributionCount']
        if count > 0:
            # Position enemies based on contribution count
            x = (i * 25) % (width - 50) + 25
            y = (i * 7) % 150 + 50
            size = min(5 + count * 2, 20)
            color = get_contribution_color(count)
            enemies.append({'x': x, 'y': y, 'size': size, 'color': color, 'count': count})
    
    # Generate SVG
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .background {{ fill: #0d1117; }}
      .player {{ fill: #58a6ff; }}
      .enemy {{ stroke: #ffffff; stroke-width: 1; }}
      .bullet {{ fill: #f85149; }}
      .stats {{ fill: #58a6ff; font-family: monospace; font-size: 14px; }}
      .title {{ fill: #c9d1d9; font-family: monospace; font-size: 16px; font-weight: bold; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect class="background" width="{width}" height="{height}"/>
  
  <!-- Stars background -->
'''
    
    # Add stars
    random.seed(42)
    for _ in range(50):
        star_x = random.randint(0, width)
        star_y = random.randint(0, height)
        svg += f'  <circle cx="{star_x}" cy="{star_y}" r="1" fill="#c9d1d9" opacity="0.5"/>\n'
    
    svg += '\n  <!-- Title -->\n'
    svg += f'  <text class="title" x="10" y="25">GitHub Contributions Space Shooter</text>\n'
    svg += f'  <text class="stats" x="10" y="45">Total Contributions: {total_contributions}</text>\n'
    
    # Add enemies
    svg += '\n  <!-- Enemies (Contribution Days) -->\n'
    for i, enemy in enumerate(enemies):
        animation_delay = i * 0.1
        svg += f'''  <g>
    <circle class="enemy" cx="{enemy['x']}" cy="{enemy['y']}" r="{enemy['size']}" fill="{enemy['color']}" opacity="0.8">
      <animate attributeName="cy" from="{enemy['y']}" to="{enemy['y'] + 200}" dur="3s" begin="{animation_delay}s" repeatCount="indefinite"/>
    </circle>
    <text x="{enemy['x']}" y="{enemy['y'] + 5}" fill="#ffffff" font-size="10" text-anchor="middle" font-family="monospace">
      {enemy['count']}
      <animate attributeName="y" from="{enemy['y'] + 5}" to="{enemy['y'] + 205}" dur="3s" begin="{animation_delay}s" repeatCount="indefinite"/>
    </text>
  </g>
'''
    
    # Add player ship
    svg += '\n  <!-- Player Ship -->\n'
    svg += f'''  <g>
    <polygon class="player" points="{player_x},{player_y} {player_x-15},{player_y+20} {player_x+15},{player_y+20}">
      <animate attributeName="points" 
               values="{player_x},{player_y} {player_x-15},{player_y+20} {player_x+15},{player_y+20};
                       {player_x+100},{player_y} {player_x+85},{player_y+20} {player_x+115},{player_y+20};
                       {player_x},{player_y} {player_x-15},{player_y+20} {player_x+15},{player_y+20}"
               dur="5s" repeatCount="indefinite"/>
    </polygon>
  </g>
'''
    
    # Add bullets
    svg += '\n  <!-- Bullets -->\n'
    for i in range(5):
        bullet_x = player_x + (i * 30 - 60)
        bullet_delay = i * 0.4
        svg += f'''  <circle class="bullet" cx="{bullet_x}" cy="{player_y}" r="3">
    <animate attributeName="cy" from="{player_y}" to="0" dur="1s" begin="{bullet_delay}s" repeatCount="indefinite"/>
    <animate attributeName="cx" from="{bullet_x}" to="{bullet_x + 100}" dur="5s" begin="{bullet_delay}s" repeatCount="indefinite"/>
  </circle>
'''
    
    svg += '</svg>'
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(svg)
    
    print(f"Space shooter animation generated: {output_file}")
    print(f"Total contributions: {total_contributions}")
    print(f"Enemies generated: {len(enemies)}")

def get_contribution_color(count):
    """Get color based on contribution count (similar to GitHub's contribution graph)."""
    if count == 0:
        return '#161b22'
    elif count < 3:
        return '#0e4429'
    elif count < 6:
        return '#006d32'
    elif count < 9:
        return '#26a641'
    else:
        return '#39d353'

def main():
    # Get username from GitHub context
    github_repository = os.environ.get('GITHUB_REPOSITORY', '')
    if github_repository:
        username = github_repository.split('/')[0]
    else:
        # Fallback to repository owner if running locally
        # This is specific to the vishalssh/vishalssh repository
        username = os.environ.get('GITHUB_USER', 'vishalssh')
    
    token = os.environ.get('GITHUB_TOKEN')
    
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        return
    
    print(f"Fetching contributions for user: {username}")
    contributions_data = fetch_github_contributions(username, token)
    
    if contributions_data:
        generate_space_shooter_svg(contributions_data)
    else:
        print("Failed to generate animation")

if __name__ == '__main__':
    main()

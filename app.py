#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import collections
collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.app_context().push()
db = SQLAlchemy(app)


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    seeking_description = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean)
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue', cascade='all, delete')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_Venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', cascade='all, delete')

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key = True)
    start_time = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id',ondelete="SET NULL",onupdate="cascade"))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id',ondelete="SET NULL", onupdate="cascade"))

migrate = Migrate(app, db)
# db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Get a list of all unique city-state pairs from the Venue table
  city_state_pairs = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

  # Create a list to store information about Venues for each pair
  venue_data = []

  # For each city-state pair, get the Venues and their upcoming show count
  for pair in city_state_pairs:
      # Create a dictionary to store information about the city-state pair
      pair_info = {}
      pair_info['city'] = pair[0]
      pair_info['state'] = pair[1]
      
      # Get the Venues for this pair
      try:
          venues = Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.city == pair[0], Venue.state == pair[1]).all()
      except:
          venues = []
      
      # Create a list to store information about each Venue for this pair
      venues_list = []
      
      # For each Venue, get the number of upcoming shows and store the information
      for venue in venues:
          venue_info = {}
          try:
              venue_info['num_upcoming_shows'] = Show.query.filter(Show.Venue_id == venue[0], Show.start_date > date.now()).count()
          except:
              venue_info['num_upcoming_shows'] = 0
          venue_info['id'] = venue[0]
          venue_info['name'] = venue[1]
          venues_list.append(venue_info)
      
      # Store the information about the Venues for this pair in the pair_info dictionary
      pair_info['venues'] = venues_list
      
      # Store the pair_info dictionary in the venue_data list
      venue_data.append(pair_info)
      
  # Pass the venue_data list to the Venues.html template
  return render_template('pages/Venues.html', areas=venue_data)

# def Venues():
#   # TODO: replace with real Venues data.
#   #       num_upcoming_shows should be aggregated based on number of upcoming shows per Venue.
#   data=[{
#     "city": "San Francisco",
#     "state": "CA",
#     "Venues": [{
#       "id": 1,
#       "name": "The Musical Hop",
#       "num_upcoming_shows": 0,
#     }, {
#       "id": 3,
#       "name": "Park Square Live Music & Coffee",
#       "num_upcoming_shows": 1,
#     }]
#   }, {
#     "city": "New York",
#     "state": "NY",
#     "Venues": [{
#       "id": 2,
#       "name": "The Dueling Pianos Bar",
#       "num_upcoming_shows": 0,
#     }]
#   }]
#   return render_template('pages/Venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_Venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # Get the search term from the search bar and make it case-insensitive
  try:
    # Get the search term from the search bar and make it case-insensitive
    search_term = request.form.get('search_term', '')
    # Filter the venues based on whether their name contains the search term
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()

    # Create a response object containing the count and data
    response = {
      "count": len(venues),
      "data": [{
        "id": venue.id,
        "name": venue.name
        } for venue in venues]
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)
  except Exception as e:
    print(e)
    flash('An error occurred. Please try again later.')
    return redirect(url_for('index'))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue is None:
        flash('Venue does not exist')
        return render_template('pages/home.html')

    upcoming_shows_query = (
        Show.query.join(Artist)
        .filter(Show.start_time > datetime.now(), Show.venue_id == venue_id)
        .all()
    )
    upcoming_shows = [
        {
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': str(show.start_time),
        }
        for show in upcoming_shows_query
    ]

    past_shows_query = (
        Show.query.join(Artist)
        .filter(Show.start_time < datetime.now(), Show.venue_id == venue_id)
        .all()
    )
    past_shows = [
        {
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': str(show.start_time),
        }
        for show in past_shows_query
    ]

    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows),
    }
    form = VenueForm(obj=venue)

    return render_template('pages/show_venue.html', venue=data, form=form)

# def show_Venue(Venue_id):
#   # shows the Venue page with the given Venue_id
#   # TODO: replace with real Venue data from the Venues table, using Venue_id
#   data1={
#     "id": 1,
#     "name": "The Musical Hop",
#     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
#     "address": "1015 Folsom Street",
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "123-123-1234",
#     "website": "https://www.themusicalhop.com",
#     "facebook_link": "https://www.facebook.com/TheMusicalHop",
#     "seeking_talent": True,
#     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
#     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
#     "past_shows": [{
#       "artist_id": 4,
#       "artist_name": "Guns N Petals",
#       "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
#       "start_time": "2019-05-21T21:30:00.000Z"
#     }],
#     "upcoming_shows": [],
#     "past_shows_count": 1,
#     "upcoming_shows_count": 0,
#   }
#   data2={
#     "id": 2,
#     "name": "The Dueling Pianos Bar",
#     "genres": ["Classical", "R&B", "Hip-Hop"],
#     "address": "335 Delancey Street",
#     "city": "New York",
#     "state": "NY",
#     "phone": "914-003-1132",
#     "website": "https://www.theduelingpianos.com",
#     "facebook_link": "https://www.facebook.com/theduelingpianos",
#     "seeking_talent": False,
#     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
#     "past_shows": [],
#     "upcoming_shows": [],
#     "past_shows_count": 0,
#     "upcoming_shows_count": 0,
#   }
#   data3={
#     "id": 3,
#     "name": "Park Square Live Music & Coffee",
#     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
#     "address": "34 Whiskey Moore Ave",
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "415-000-1234",
#     "website": "https://www.parksquarelivemusicandcoffee.com",
#     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
#     "seeking_talent": False,
#     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#     "past_shows": [{
#       "artist_id": 5,
#       "artist_name": "Matt Quevedo",
#       "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
#       "start_time": "2019-06-15T23:00:00.000Z"
#     }],
#     "upcoming_shows": [{
#       "artist_id": 6,
#       "artist_name": "The Wild Sax Band",
#       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#       "start_time": "2035-04-01T20:00:00.000Z"
#     }, {
#       "artist_id": 6,
#       "artist_name": "The Wild Sax Band",
#       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#       "start_time": "2035-04-08T20:00:00.000Z"
#     }, {
#       "artist_id": 6,
#       "artist_name": "The Wild Sax Band",
#       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#       "start_time": "2035-04-15T20:00:00.000Z"
#     }],
#     "past_shows_count": 1,
#     "upcoming_shows_count": 1,
#   }
#   data = list(filter(lambda d: d['id'] == Venue_id, [data1, data2, data3]))[0]
#   return render_template('pages/show_Venue.html', Venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_Venue_form():
  form = VenueForm()
  return render_template('forms/new_Venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_Venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    # Get form data
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
        
    # Create new Venue object
    venue = Venue(
      name=name,
      city=city,
      state=state,
      address=address,
      phone=phone,
      image_link=image_link,
      genres=genres,
      facebook_link=facebook_link
    )
        
    # Add and commit new Venue record to the database
    db.session.add(venue)
    db.session.commit()
        
    # Flash success message
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # Rollback if there's any error
    db.session.rollback()
    error = True
    # Flash error message
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    # Close database session
    db.session.close()
        
  if error:
    # If there's an error, redirect to home page
    return render_template('pages/home.html')
  else:
    # If successful, redirect to Venues page
    return redirect(url_for('venues'))

@app.route('/Venues/<Venue_id>', methods=['DELETE'])
def delete_Venue(Venue_id):
  # TODO: Complete this endpoint for taking a Venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id = venue_id).delete()
    db.session.commit()
    db.session.close()
    flash('The Venue was deleted successfully!.')
    return jsonify({'success': True}) 
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. could not delete the venue.')
    db.session.close()
    return jsonify({'success': False}) 
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # Retrieve data from the Artist table
  artists = Artist.query.all()

  # Format data as a list of dictionaries
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
        "name": artist.name,
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response = {
    "count": len(artists),
    "data": []
  }

  for artist in artists:
    response["data"].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(artist.shows)
    })

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # get artist by id
  artist = Artist.query.get(artist_id)

  # get past shows
  past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
  filter(
    Show.artist_id == artist_id,
    Show.venue_id == Venue.id,
    Show.start_time < datetime.now()
  ).all()

  # get upcoming shows
  upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
  filter(
    Show.artist_id == artist_id,
    Show.venue_id == Venue.id,
    Show.start_time > datetime.now()
  ).all()

  # format past shows
  past_shows_list = []
  for venue, show in past_shows:
    past_shows_list.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": format_datetime(str(show.start_time))
    })

  # format upcoming shows
  upcoming_shows_list = []
  for venue, show in upcoming_shows:
    upcoming_shows_list.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": format_datetime(str(show.start_time))
    })

  # format artist data
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_Venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows_list,
    "upcoming_shows": upcoming_shows_list,
    "past_shows_count": len(past_shows_list),
    "upcoming_shows_count": len(upcoming_shows_list)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_Venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  try:
    artist.name = form.name.data
    artist.genres = ','.join(form.genres.data)
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_Venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.image_link = form.image_link.data

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))

  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')

  finally:
    db.session.close()

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # Retrieve the Venue object with the specified ID from your data source
  venue = Venue.query.get(venue_id)
  # Pre-populate the form fields with the values from the Venue object
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  # form.website.data = venue.website,
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link
  # TODO: populate form with values from Venue with ID <Venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # Venue record with ID <Venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  try:
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website = form.website.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be updated.')
  finally:
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # Get the form data
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  # website = request.form['website']
  facebook_link = request.form['facebook_link']
  seeking_Venue = True if 'seeking_Venue' in request.form else False
  seeking_description = request.form['seeking_description']
  image_link = request.form['image_link']

  # Create a new Artist object with the form data
  new_artist = Artist(
        name=name,
        city=city,
        state=state,
        phone=phone,
        genres=genres,
        # website=website,
        facebook_link=facebook_link,
        seeking_Venue=seeking_Venue,
        seeking_description=seeking_description,
        image_link=image_link
  )

  # Insert the new Artist object into the database
  try:
    db.session.add(new_artist)
    db.session.commit()
    # Flash a success message
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    # Flash an error message
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # Retrieve all shows from the database
  shows = Show.query.all()

  # Create a list of dictionaries containing information about each show
  data = []
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    })

    # Render the shows page with the data
    return render_template('pages/shows.html', shows=data)
    
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # Retrieve form data
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']

  # Create a new Show object and add it to the database session
  show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
  db.session.add(show)

  try:
    db.session.commit()
    # If the commit is successful, flash a success message
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    # If the commit fails, flash an error message
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

    # Redirect to the home page
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

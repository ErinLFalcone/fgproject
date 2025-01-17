from model import db, User, Tile, connect_to_db
import random as r

def create_user(username, password, win_count=0, in_game=False):
    """Create and return a new user."""

    new_user = User(username=username,
        password=password,
        win_count=win_count,
        in_game=in_game
        )

    db.session.add(new_user)
    db.session.commit()

    return new_user

def create_tile(x_cord, y_cord, username, is_mine=False, mine_count=0, is_viewed=False, is_flag=False):
    """Create and return a new tile."""

    new_tile = Tile(
        x_cord=x_cord,
        y_cord=y_cord,
        username=username,
        is_mine=is_mine,
        mine_count=mine_count,
        is_viewed=is_viewed,
        is_flag=is_flag
        )

    db.session.add(new_tile)
    db.session.commit()

    return new_tile

def adj_mine_setter(first_tile, last_tile, mine_list, username):
    """Called in fill_new_game(). Takes in the first and last tiles and the list of mine tiles,
    computes the number of mine tiles adjacent to all non-mine tiles
    and updates the tile database with this information."""


    # Loops through each tile in the database by ID. If the tile is not a mine,
    # checks all tiles with an x,y cord from (x-1),(y-1) to (x+1),(y+1)
    # (which is the 3x3 grid surrounding the tile)
    # for mines, and adds up that number. 
    for i in range(first_tile.tile_id,last_tile.tile_id):
        if i not in mine_list:
            tile_mine_count = 0
            not_mine = Tile.query.filter_by(
                tile_id = i,
                username = username
                ).first()
            nm_x = not_mine.x_cord
            nm_y = not_mine.y_cord

            check_x_cord = nm_x-1
            while check_x_cord <= nm_x+1:
                check_y_cord = nm_y-1
                while check_y_cord <= nm_y+1:
                    check_tile = Tile.query.filter_by(
                        x_cord=check_x_cord, y_cord=check_y_cord,
                        username=username
                        ).first()
                    try:
                        if check_tile.is_mine == True:
                            tile_mine_count+=1
                    except:
                        pass
                    check_y_cord +=1
                check_x_cord +=1

            # Updates the database with the total adjacent mines found for the tile
            setattr(not_mine, 'mine_count', tile_mine_count)
            db.session.commit()


def adj_z_mine_add(tile_obj_dict, z_mine_obj, username):
    """Called in fill_z_tile_dict. Takes in a dictionary of non-mine Tile objects
    and a single Tile object that has zero adjacent mines.
    Checks all tiles adjacent to the zero adjacent mine Tile object,
    and adds those tiles to the non-mine tile dictionary.
    Returns the non-mine tile dictionary. 
    """

    update_dict = tile_obj_dict
    z_mine_obj = z_mine_obj

    # Add all adjacent tiles to dictionary
    zm_x = z_mine_obj.x_cord
    zm_y = z_mine_obj.y_cord
    adj_x_cord = zm_x-1

    while adj_x_cord <= zm_x+1:
        adj_y_cord = zm_y-1
        while adj_y_cord <= zm_y+1:
            adj_tile = Tile.query.filter_by(
                x_cord=adj_x_cord, y_cord=adj_y_cord,
                username=username
                ).first()
            if (
                adj_tile not in tile_obj_dict
                ) and (
                    adj_tile is not None
                    ):
                update_dict[adj_tile] = adj_tile.mine_count
                setattr(adj_tile, 'is_viewed', True)
                db.session.commit()
            adj_y_cord +=1
        adj_x_cord +=1
   
    return update_dict

def fill_z_tile_dict(z_mine_obj, username):
    """Called when a tile with zero adjacent mines is clicked on in game.
    Takes in the zero adjacent mine Tile object
    and fills in a dictionary of all connecting zero mine tiles,
    as well as tiles bordering those, with a value for the number of adjacent mines.
    Returns a dictionary of those non-mine Tile objects, and adjacent mine values."""


    tile_obj_dict = {z_mine_obj : 0}
    update_dict = {}
    checked_set = set([])

    setattr(z_mine_obj, 'is_viewed', True)
    db.session.commit()

    while True:
        update_dict.update(tile_obj_dict)
        for tile in tile_obj_dict:
            if (tile_obj_dict[tile] == 0) and (tile not in checked_set):
                checked_set.add(tile)
                update_dict.update(
                    adj_z_mine_add(update_dict, tile, username)
                    )

        if len(tile_obj_dict) == len(update_dict):
            break
        else:
            tile_obj_dict.update(update_dict)


    return tile_obj_dict

def fill_new_game(username, num_mine=60):
    """Takes in desired number of mine tiles (defaulting to 60)
    and refreshes the mines and adjacent mine numbers in the database.
    """

    # Deletes old game tiles
    Tile.query.filter_by(username=username).delete()
    db.session.commit()

    x_cord = 0

    while x_cord <= 29:
        y_cord = 0
        while y_cord <= 19:
            create_tile(x_cord, y_cord, username)
            y_cord +=1
        x_cord +=1


    first_tile = Tile.query.filter_by(username=username).order_by(Tile.tile_id).first()

    last_tile = Tile.query.filter_by(username=username).order_by(Tile.tile_id.desc()).first()
    
    mine_list = r.sample(range(first_tile.tile_id,last_tile.tile_id), num_mine)

    # remove old mines
    curr_mines = Tile.query.filter_by(is_mine=True, username=username).all()
    for mine in curr_mines:
        setattr(mine, 'is_mine', False)
        db.session.commit()

    # remove viewed tiles
    viewed_tiles = Tile.query.filter_by(is_viewed=True, username=username).all()
    for viewed in viewed_tiles:
        setattr(viewed, 'is_viewed', False)
        db.session.commit()

    for mine in mine_list:
        mine_tile = Tile.query.filter_by(
            tile_id = mine,
            username = username
            ).first()
        setattr(mine_tile, 'is_mine', True)
        db.session.commit()

    adj_mine_setter(first_tile, last_tile, mine_list, username)

def read_user(username):
    """Takes in a username, queries the database,
    and returns the User object"""

    user = User.query.filter(
        User.username == username
        ).first()

    return user

def read_tile(tile_x, tile_y, username):
    """Takes in an x,y coordinate and
    returns the Tile object for that coordinate"""
   
    tile = Tile.query.filter_by(
        x_cord = tile_x,
        y_cord = tile_y,
        username = username
        ).first()

    setattr(tile, 'is_viewed', True)
    setattr(tile, 'is_flagged', False)
    db.session.commit()

    return tile

def read_all_mines(username):
    """Queries the database for all mine tiles,
    returns that data as a list of Tile objects"""

    all_mines = Tile.query.filter_by(username=username, is_mine = True).all()

    return all_mines

def read_viewed_tiles(username):
    """Takes in a username,
    returns list of tiles in active game where is_viewed=True"""

    tile_objs = Tile.query.filter_by(
                username=username, is_viewed=True, is_mine=False
                ).all()

    tile_objs.extend(Tile.query.filter_by(
                username=username, is_flag=True
                ).all())

    viewed_list = []
         
    for obj in tile_objs:
        if obj.is_flag is True:
            new_list = [obj.x_cord, obj.y_cord, "🚩"]
        else:
            new_list = [obj.x_cord, obj.y_cord, obj.mine_count]
        viewed_list.append(new_list)

    return viewed_list


def increment_wins(username):
    """Increment win count for a given uyser by 1"""

    user = User.query.filter(
        User.username == username
        ).first()

    new_wins = user.win_count +1

    setattr(user, 'win_count', new_wins)
    db.session.commit()
    print(user.win_count)

    return user.win_count

def set_in_game(username):
    """Sets game state to True for given user."""

    user = User.query.filter(
        User.username == username
        ).first()

    setattr(user, 'in_game', True)
    db.session.commit()

def set_not_in_game(username):
    """Sets game state to False for given user."""

    user = User.query.filter(
        User.username == username
        ).first()

    setattr(user, 'in_game', False)
    db.session.commit()

def flag_tile(tile):
    """Sets the is_flag column to true for given tile."""

    setattr(tile, 'is_flag', True)
    db.session.commit()

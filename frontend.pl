#!/usr/bin/env perl
use Dancer2;
use DBI;

# Connect to the SQLite database
my $dbh = DBI->connect("dbi:SQLite:dbname=xkcd_game.db", "", "", {
    RaiseError => 1,
    AutoCommit => 1,
});

# Home route to display AI-generated image and guess options
get '/' => sub {
    # Fetch a random image from the database
    my $sth = $dbh->prepare("SELECT * FROM images ORDER BY RANDOM() LIMIT 1");
    $sth->execute();
    my $image = $sth->fetchrow_hashref;

    # Fetch 3 wrong comic options and 1 correct option
    my $correct_comic_id = $image->{correct_comic_id};
    $sth = $dbh->prepare("SELECT * FROM comics WHERE comic_id != ? ORDER BY RANDOM() LIMIT 3");
    $sth->execute($correct_comic_id);
    my @wrong_comics = @{ $sth->fetchall_arrayref({}) };

    # Fetch the correct comic option
    $sth = $dbh->prepare("SELECT * FROM comics WHERE comic_id = ?");
    $sth->execute($correct_comic_id);
    my $correct_comic = $sth->fetchrow_hashref;

    # Combine options and shuffle them
    push @wrong_comics, $correct_comic;
    @wrong_comics = sort { rand() <=> rand() } @wrong_comics;

    # Render the page with image and options
    template 'index' => { image => $image, options => \@wrong_comics };
};

# Post route to handle user's guess
post '/guess' => sub {
    my $user_id = body_parameters->get('user_id');
    my $image_id = body_parameters->get('image_id');
    my $guessed_comic_id = body_parameters->get('guessed_comic_id');

    # Check if the guess is correct
    my $sth = $dbh->prepare("SELECT correct_comic_id FROM images WHERE image_id = ?");
    $sth->execute($image_id);
    my $correct_comic_id = $sth->fetchrow_array;

    my $is_correct = ($guessed_comic_id == $correct_comic_id) ? 1 : 0;

    # Update the image statistics
    $sth = $dbh->prepare("UPDATE images SET total_attempts = total_attempts + 1 WHERE image_id = ?");
    $sth->execute($image_id);

    if ($is_correct) {
        $sth = $dbh->prepare("UPDATE images SET correct_attempts = correct_attempts + 1 WHERE image_id = ?");
        $sth->execute($image_id);
    }

    # Calculate the difficulty-based score
    $sth = $dbh->prepare("SELECT correct_attempts, total_attempts FROM images WHERE image_id = ?");
    $sth->execute($image_id);
    my ($correct_attempts, $total_attempts) = $sth->fetchrow_array;
    my $percentage_correct = ($total_attempts > 0) ? ($correct_attempts / $total_attempts) : 0;
    my $base_score = 100;
    my $score = int($base_score / ($percentage_correct + 0.1));  # Avoid division by 0

    # Update the user's score
    if ($is_correct) {
        $sth = $dbh->prepare("UPDATE users SET total_score = total_score + ? WHERE user_id = ?");
        $sth->execute($score, $user_id);
    }

    # Log the user's guess
    $sth = $dbh->prepare("INSERT INTO guesses (user_id, image_id, guessed_comic_id, is_correct) VALUES (?, ?, ?, ?)");
    $sth->execute($user_id, $image_id, $guessed_comic_id, $is_correct);

    # Redirect to the home page after the guess
    redirect '/';
};

# Start the Dancer2 app
start;

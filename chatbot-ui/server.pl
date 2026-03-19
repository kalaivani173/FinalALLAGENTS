use strict;
use warnings;
use HTTP::Server::Simple::CGI;
use File::Spec;
use POSIX qw();

my $port = $ENV{PORT} || 5500;

package MyServer;
use base 'HTTP::Server::Simple::CGI';

sub handle_request {
    my ($self, $cgi) = @_;
    my $path = $cgi->path_info();
    $path = '/index.html' if $path eq '/' || $path eq '';

    my $base = 'C:/Users/localadmin/Desktop/Projects/FinalALLAGENTS/chatbot-ui';
    $path =~ s|/|\\|g if $^O eq 'MSWin32';
    my $file = $base . $path;

    if (-f $file) {
        my $ct = 'text/html; charset=utf-8';
        $ct = 'application/javascript' if $file =~ /\.js$/;
        $ct = 'text/css' if $file =~ /\.css$/;
        print "HTTP/1.1 200 OK\r\n";
        print "Content-Type: $ct\r\n\r\n";
        open my $fh, '<:raw', $file or die;
        print while <$fh>;
        close $fh;
    } else {
        print "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n404";
    }
}

package main;
my $server = MyServer->new($port);
print "Server started on port $port\n";
$server->run();

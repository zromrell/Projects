function bridgeMap
    
    name = '9_3';
    numx = [0 1 0.3726 0.3579 0.9499 0.2334 0.7691 0.6921 0.229 0.8835 0];
    numy = [0 0 0.7787 0.5575 0.5867 -0.0872 0.3278 0.5773 0.8554 0.3553 0];
    numz = [0 0 0 -0.9751 -0.1697 -0.3496 0.3857 -0.5795 0.2619 -0.3051 0];
    graphBridge(numx, numy, numz, name);
    
    name = '3_1';
    numx = [0.96592582628 0.2588190451 -0.70710678118 0.70710678118 -0.2588190451 -0.96592582628 0.96592582628];
    numy = [-0.2588190451 0.96592582628 -0.70710678118 -0.70710678118 0.96592582628 -0.2588190451 -0.2588190451];
    numz = [-1 1 -1 1 -1 1 -1];
    graphBridge(numx, numy, numz, name);  
    
end

 
function bridgeMap = graphBridge(a, b, c, name) 
    
    %check to make sure have proper coordinates
    if length(a) ~= length(b)
        display("x length is not equivalent to y length");
        exit;
    elseif length(b) ~= length(c)
        display("y length is not equivalent to z length");
        exit;
    elseif length(c) ~= length(a)
        display("z length is not equivalent to x length");
        exit;
    end

    %number of sticks
    disp("Stick Number:");
    disp(length(a)-1 );
    
    
    %lists for coordinates of stick knot
    xcoord = [] * length(a);
    ycoord = [] * length(b);
    zcoord = [] * length(c);
    %multiply coordinates by 1000
    for i = 1:(length(a))
        xcoord(i) = 1000 * a(i);
        ycoord(i) = 1000 * b(i);
        zcoord(i) = 1000 * c(i);
        %when testing coordinates which are already scaled up
        %xcoord(i) = 1 * a(i);
        %ycoord(i) = 1 * b(i);
        %zcoord(i) = 1 * c(i);
    end
    
    
    %tantrix coordinates
    xtantrix = []*length(xcoord);
    ytantrix = []*length(ycoord);
    ztantrix = []*length(zcoord);

    %computes tantrix coordinates
    for i = 1:(length(zcoord)-1)
        xtantrix(i) = xcoord(i+1) - xcoord(i);
        ytantrix(i) = ycoord(i+1) - ycoord(i);
        ztantrix(i) = zcoord(i+1) - zcoord(i);
        magnitude = sqrt(sum([xtantrix(i); ytantrix(i); ztantrix(i)].^2,1));
        xtantrix(i) = xtantrix(i)/magnitude;
        ytantrix(i) = ytantrix(i)/magnitude;
        ztantrix(i) = ztantrix(i)/magnitude;
    end
    %creates a cycle of indices
    xtantrix(end+1) = xtantrix(1);
    ytantrix(end+1) = ytantrix(1);
    ztantrix(end+1) = ztantrix(1);
    
    %computes anit-tantrix
    xxtantrix = []*length(xtantrix);
    yytantrix = []*length(xtantrix);
    zztantrix = []*length(xtantrix);
    for i = 1:length(xtantrix)
        xxtantrix(i) = -1 * xtantrix(i);
        yytantrix(i) = -1 * ytantrix(i);
        zztantrix(i) = -1 * ztantrix(i);
    end
    
    
    %computes tantrix length
    len_tan = findLength(xtantrix, ytantrix, ztantrix);
    %display(len_tan); 
    
    
    
    %Computes binotrix and normalizes
    xbinotrix = []*length(xtantrix);
    ybinotrix = []*length(ytantrix);
    zbinotrix = []*length(ztantrix);
    for i = 1:(length(ztantrix)-1)
        xbinotrix(i) = ytantrix(i)*ztantrix(i+1) - ytantrix(i+1)*ztantrix(i);
        ybinotrix(i) = xtantrix(i)*ztantrix(i+1) - xtantrix(i+1)*ztantrix(i);
        zbinotrix(i) = xtantrix(i)*ytantrix(i+1) - xtantrix(i+1)*ytantrix(i);
        magnitude = sqrt(sum([xbinotrix(i); ybinotrix(i); zbinotrix(i)].^2,1));
        xbinotrix(i) = xbinotrix(i)/magnitude;
        ybinotrix(i) = ybinotrix(i)/magnitude;
        zbinotrix(i) = zbinotrix(i)/magnitude;
    end
    %creates cycle of indices
    xbinotrix(end+1) = xbinotrix(1);
    ybinotrix(end+1) = ybinotrix(1);
    zbinotrix(end+1) = zbinotrix(1);
    
    %computes anti-binotrix coordinates
    xxbinotrix = []*length(xbinotrix);
    yybinotrix = []*length(ybinotrix);
    zzbinotrix = []*length(zbinotrix);
    for i = 1:length(zbinotrix)
        xxbinotrix(i) = -1 * xbinotrix(i);
        yybinotrix(i) = -1 * ybinotrix(i);
        zzbinotrix(i) = -1 * zbinotrix(i);
    end
    
    
    %copmutes length of binotrix
    len_bin = findLength(xbinotrix, ybinotrix, zbinotrix);
    %display(len_bin)
    

    % milnor curvature invariant calculation
    milnor = len_tan + len_bin;
    display(milnor/(2*pi));
    
    
    
    %scales stick knot coordinates down
    for i = 1:(length(xcoord))
        xcoord(i) = xcoord(i)/2000;
        ycoord(i) = -1*ycoord(i)/2000;
        zcoord(i) = zcoord(i)/2000;
    end
    
    
    % random test: curvature + torsion
    %{
    xsum1 = []*length(xbinotrix);
    ysum1 = []*length(ybinotrix);
    zsum1 = []*length(zbinotrix);
    for i = 1:(length(zbinotrix))
        xsum1(i) = xbinotrix(i) + xtantrix(i);
        ysum1(i) = ybinotrix(i) + ytantrix(i);
        zsum1(i) = zbinotrix(i) + ztantrix(i);
    end
    xsum2 = []*length(xbinotrix);
    ysum2 = []*length(ybinotrix);
    zsum2 = []*length(zbinotrix);
    for i = 1:(length(zbinotrix))
        xsum2(i) = xxbinotrix(i) + xtantrix(i);
        ysum2(i) = yybinotrix(i) + ytantrix(i);
        zsum2(i) = zzbinotrix(i) + ztantrix(i);
    end
    %}
  
    
    %
    %GRAPHING
    %
    
    
    %constants
    figure('Name', name)
    axis([-2 2 -2 2 -2 2]); axis square; hold on
    acc = 100; % accuracy: ~ lines per arc
    %labels = {'1', '2', '3', '4', '5', '6'};
    
    %plots stick knot
    %plot3(xcoord,ycoord,zcoord,'.b');
    %text(xcoord, ycoord, zcoord, labels)
    plot3(xcoord',ycoord',zcoord','b');
    
    %plots stick version and points of binotrix 
    %plot3(xbinotrix',ybinotrix',zbinotrix','r');
    %plots arcs of binotrix on unit sphere
    V = track_arc(xbinotrix,ybinotrix,zbinotrix,acc);
    plot3(V(1,:),V(2,:),V(3,:),'w');
    
    %plots stick version and points of anti-binotrix
    %plot3(xxbinotrix',yybinotrix',zzbinotrix','r');
    %plots arcs of anit-binotrix on unit sphere
    V = track_arc(xxbinotrix,yybinotrix,zzbinotrix,acc);
    plot3(V(1,:),V(2,:),V(3,:),'w');
    
    
    %plots stick version and points of tantrix
    %plot3(xtantrix',ytantrix',ztantrix','r');
    %plots arcs of tantrix on unit sphere
    %V = track_arc(xtantrix,ytantrix,ztantrix,acc);
    %plot3(V(1,:),V(2,:),V(3,:),'w');
    
    
    %plots stick version and points of tantrix
    %plot3(xxtantrix',yytantrix',zztantrix','g');
    %plots arcs of tantrix on unit sphere
    %V = track_arc(xxtantrix,yytantrix,zztantrix,acc);
    %plot3(V(1,:),V(2,:),V(3,:),'w');
    
   
    %random test: tantrix + binotrix 
    %plot3(xsum1,ysum1,zsum1,'.m');
    %plot3(xsum1',ysum1',zsum1','m');
    %plot3(xsum2,ysum2,zsum2,'.m');
    %plot3(xsum2',ysum2',zsum2','m');
    
    
    %view(90,0)
    %set(gca,'CameraViewAngle', 15)
    

    [x3 y3 z3] = sphere();
    h = surfl(x3, y3, z3); 
    set(h, 'FaceAlpha', 0.1)
    colormap([1 1 1]*0.1)
    shading interp
    view(-37.5, 30)
    
    
    %sphere(31)
    %colormap([1 1 1]*0.1) 
end

function val = findLength(a,b,c)
    total = 0;
    for i = 1:(length(c)-1)
        current = acos(a(i)*a(i+1) + b(i)*b(i+1) + c(i)*c(i+1));
        total = total + current;
    end
    val = total;
end
    
function V = track_arc(x,y,z,acc)
    v1 = [x(1:end-1);y(1:end-1);z(1:end-1)]; % Vector from center to 1st point
    v2 = [x(2:end);y(2:end);z(2:end)]; % Vector from center to 2nd point
    r = sqrt(sum([x(1); y(1); z(1)].^2,1));
    v3a = cross(cross(v1,v2),v1); % v3 lies in plane of v1 & v2 and is orthog. to v1
    v3 = r*v3a./repmat(sqrt(sum(v3a.^2,1)),3,1); % Make v3 of length r
    % Let t range through the inner angle between v1 and v2
    tmax = atan2(sqrt(sum(cross(v1,v2).^2,1)),dot(v1,v2));
    V = zeros(3,sum(round(tmax*acc))); % preallocate
    k = 0; % index in v
    for i = 1:length(tmax)
        steps = round(tmax(i)*acc)+1; %Edited +1
        k = (1:steps) + k(end);
        t = linspace(0,tmax(i),steps);
        V(:,k) = v1(:,i)*cos(t)+v3(:,i)*sin(t);
    end
end

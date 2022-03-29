function matlab_send_transform()

udps = dsp.UDPSender( ...
    'RemoteIPPort', 8059, ...
    'RemoteIPAddress', '127.0.0.1' ...
    );
cleanupObj = onCleanup(@()cleanMeUp(udps));
t = 0;
while 1
    dataSent = uint8(append('_transf___',num2str(t)));
    udps(dataSent);
    pause(0.001);
    t = t+0.001;
end
end

function cleanMeUp(udps)

end

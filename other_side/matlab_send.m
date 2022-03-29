function matlab_send()

udps = dsp.UDPSender( ...
    'RemoteIPPort', 8059, ...
    'RemoteIPAddress', '127.0.0.1' ...
    );
cleanupObj = onCleanup(@()cleanMeUp(udps));
ctr = 0;
while 1
    ctr = ctr+1;
    dataSent = uint8(append('_transf___','1.0_',num2str(ctr)));
    udps(dataSent);
    pause(0.001);
end
end

function cleanMeUp(udps)

end
